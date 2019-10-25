import numpy as np
import pandas as pd

class Incident:

    # Incident variables
    incident_id = None
    intervention_main_row = None
    intervention_main_row_index = None
    intervention_phase_label = None
    incident_main_rows = None
    incident_detail_rows = None
    intervention_cycle_start = None
    incident_cycle_interval = None
    incident_cycle_interval_phase_sums = None
    incident_cycle_phase_durations = None
    incident_cycle_phase_labels = None
    incident_cycle_timecomp = None
    intervention_cycle_sequence_overview = None
    NO_CYCLE_INTERVALS = None
    is_complete = False
    ev_accepted = None
    ev_eta = None
    ev_running = None
    ev_cancelled = None
    ev_terminated = None
    ev_complete_time = None
    ev_complete_time_state = None
    ev_status_datetimes = None
    TMREVPVIZ_ERROR_LOGGER = None

    def __init__(self, incident_id, incident_detail_rows, csv_main, NO_CYCLE_INTERVALS, logger):
        self.TMREVPVIZ_ERROR_LOGGER = logger
        self.incident_id = incident_id
        self.incident_detail_rows = incident_detail_rows.sort_values(by="Update Time")
        self.NO_CYCLE_INTERVALS = NO_CYCLE_INTERVALS

        # Check if incident is complete, if NOT: remove

        complete_check_rows = self.incident_detail_rows.copy()
        eta = complete_check_rows[complete_check_rows["Request State"] == "Running"]
        if eta.shape[0] == 0:
            self.is_complete = False
            logger.warning("Id {} did not have any 'running' states".format(self.incident_id))
            return None

        cancelled_rows = self.incident_detail_rows[self.incident_detail_rows['Request State'] == "Cancelled"]
        if cancelled_rows.shape[0] == 0:
            ev_cancelled = False
        else:
            self.ev_cancelled = cancelled_rows

        terminated_rows = self.incident_detail_rows[self.incident_detail_rows['Request State'] == "Terminated"]
        if terminated_rows.shape[0] == 0:
            ev_terminated = False
        else:
            self.ev_terminated = terminated_rows

        complete_rows = cancelled_rows.append(terminated_rows).sort_values(by="Update Time", ascending=False)
        if complete_rows.shape[0] == 0:
            self.is_complete = False
            logger.warning("Id {} did not have any 'cancelled' or 'terminated' states".format(self.incident_id))
            return None
        else:
            self.ev_complete_time = complete_rows.iloc[0]["Update Time"]
            self.ev_complete_time_state = complete_rows.iloc[0]["Request State"]

        self.set_intervention_main_row(self.ev_complete_time, csv_main)

        self.incident_main_rows = csv_main.iloc[self.intervention_main_row_index-self.NO_CYCLE_INTERVALS:self.intervention_main_row_index+self.NO_CYCLE_INTERVALS+1]

        if (type(self.intervention_main_row) == bool) and (self.intervention_main_row == False):
            # print()
            self.is_complete = False
            logger.warning("Id {} did not have enought data from CSV_MAIN to create cycle interval.".format(self.incident_id))
            return None

        else:
            self.is_complete = True

        # Find Accepted
        self.set_ev_accepted()
        # Find ETA
        eta_rows = incident_detail_rows.sort_values(by="Update Time", ascending=False)
        self.ev_eta = eta_rows[eta_rows["Request State"] == "Running"].iloc[0]["ETA"]
        # Find Running
        self.ev_running = incident_detail_rows[incident_detail_rows["Request State"] == "Running"]
        # Set incident cycle interval
        self.set_incident_cycle_interval(csv_main)
        # Set cycle phase duration and labels
        ev_labels, ev_phases = self.get_cycle_phase_values(self.intervention_main_row)
        self.incident_cycle_phase_labels = ev_labels
        self.incident_cycle_phase_durations = ev_phases
        # Set sum duration of phases
        self.set_incident_cycle_interval_phase_sums()
        # Set ev cycle time comparison
        self.set_ev_cycle_timecomp()
        # Set ev status date times df
        self.set_ev_status_datetimes()
        # Set sequence overview
        self.set_intervention_cycle_sequence_overview()


    ######################################################
    ###################### SETTERS #######################
    ######################################################


    def set_intervention_main_row(self, i_datetime, df):
        # Input: (specified date, relating main dataframe)
        # Create time interval of 10 sec
        before = i_datetime - pd.Timedelta(minutes=10)
        after = i_datetime + pd.Timedelta(minutes=10)
        rows = df[df["Time"] > before]
        rows = rows[rows["Time"] < after]
        rows = rows.sort_values(by="Time")

        if rows.shape[0] == 0:
            self.intervention_cycle_start = False
            self.intervention_main_row = False
            self.intervention_main_row_index = False
            return False

        # Set starting point for loop as the first rows' datetime
        current_datetime_row = rows.iloc[0]
        current_datetime = rows.iloc[0]["Time"]
        current_datetime_index = 0

        # Iterate through to find closest (floor) datetime]
        for index, row in rows.iterrows():
            row_datetime = row["Time"]
            row_index = index
            # If later than i_datetime stop loop
            if row_datetime > i_datetime:
                break
            # If less or the same, save for later
            current_datetime = row_datetime
            current_datetime_index = index
            current_datetime_row = row

        self.intervention_cycle_start = current_datetime
        self.intervention_main_row = current_datetime_row
        self.intervention_main_row_index = current_datetime_index

    def set_incident_cycle_interval(self, i_main):

        # Fetch interval for search
        c_interval_rows = i_main.iloc[self.intervention_main_row_index-self.NO_CYCLE_INTERVALS:self.intervention_main_row_index+self.NO_CYCLE_INTERVALS+1]

        if c_interval_rows.shape[0] == 0:
            # print("Error: Interval dataframe has 0 rows - get_incident_cycle_interval")
            return False

        self.incident_cycle_interval = c_interval_rows

    def set_incident_cycle_interval_phase_sums(self):
        i_interval = self.incident_cycle_interval.reset_index(drop=True)
        no_mid = i_interval.drop([self.NO_CYCLE_INTERVALS], axis=0)
        self.incident_cycle_interval_phase_sums = i_interval.aggregate(["mean"])

    def set_ev_cycle_timecomp(self):
        agg = self.incident_cycle_interval_phase_sums
        i_interval = self.incident_cycle_interval

        row = self.intervention_main_row
        labels = self.incident_cycle_phase_labels

        timecomp_array = []
        for c in labels:
            if not np.isnan(i_interval.iloc[self.NO_CYCLE_INTERVALS][c]):
                diff = i_interval.iloc[self.NO_CYCLE_INTERVALS][c] - agg.iloc[0][c]
                timecomp_array.append([c, i_interval.iloc[self.NO_CYCLE_INTERVALS][c], diff, agg.iloc[0][c], (i_interval.iloc[self.NO_CYCLE_INTERVALS][c] - agg.iloc[0][c])-1])
        self.incident_cycle_timecomp = timecomp_array

    def set_ev_accepted(self):
        complete_rows = self.incident_detail_rows[self.incident_detail_rows['Request State'] == "Cancelled"].append(self.incident_detail_rows[self.incident_detail_rows['Request State'] == "Terminated"])
        filtered_rows = pd.DataFrame(columns=complete_rows.columns.values)
        if complete_rows.shape[0] > 1:
            rows = self.incident_detail_rows.copy().reset_index(drop=True)
            is_ev_accepted = False
            is_ev_ended = False
            for i in range(0, rows.shape[0]):
                row = rows.iloc[i]
                if(is_ev_accepted == False) and (row['Request State'] == "Accepted"):
                    is_ev_accepted = True
                    filtered_rows = filtered_rows.append(row, ignore_index = True)
                elif (is_ev_accepted == True) and ((row['Request State'] == "Cancelled") or (row['Request State'] == "Terminated")):
                    is_ev_ended = True
                elif ((is_ev_accepted == True) and (is_ev_ended == True)) and ((row['Request State'] == "Accepted")):
                    is_ev_accepted = True
                    is_ev_ended = False
                    filtered_rows = filtered_rows.append(row, ignore_index = True)
            self.ev_accepted = filtered_rows
        else:
            filtered_rows = filtered_rows.append(self.incident_detail_rows.iloc[0], ignore_index = True)
            self.ev_accepted = filtered_rows


    def set_ev_status_datetimes(self):
        ev_accepted = self.ev_accepted
        ev_running = self.ev_running
        eta = self.ev_eta
        ev_cancelled = self.ev_cancelled
        ev_terminated = self.ev_terminated

        s_df = pd.DataFrame(columns=["status", "time"])
        statuses = [ev_accepted, ev_running, eta, ev_cancelled, ev_terminated]
        statuses_labels = ["EV Accepted", "EV Running", "EV ETA", "EV Cancelled", "EV Terminated"]
        for s_index in range(0, len(statuses)):
            if (statuses_labels[s_index] == "EV ETA"):
                s_df.loc[s_df.shape[0]] = [statuses_labels[s_index], pd.to_datetime(statuses[s_index])]
            else:
                if (type(statuses[s_index]) == pd.core.frame.DataFrame) and (len(statuses[s_index]) > 0):
                    for i in range(0, len(statuses[s_index])):
                        s_df.loc[s_df.shape[0]] = [statuses_labels[s_index], pd.to_datetime(statuses[s_index].iloc[i]["Update Time"])]
        s_df.sort_values(by="time", inplace=True)

        self.ev_status_datetimes = s_df


    def set_intervention_cycle_sequence_overview(self):
        # Get main row, cycle start value, complete time, phase durations and labels
        cycle_start = self.intervention_main_row["Time"]
        # Structure: [label, datetime, is-intervention-phase, is-eta-phase]
        sequence_overview = {}
        sequence_segments = []
        timesum = cycle_start
        intervention_index = 0
        eta_index = 0
        is_intervention_set = False
        is_eta_set = False
        for i in range(0, len(self.incident_cycle_phase_labels)):
            label = self.incident_cycle_phase_labels[i]
            time = timesum
            is_intervention = False
            is_eta = False
            timesum += pd.Timedelta(seconds=self.incident_cycle_phase_durations[i])
            if is_intervention_set == False and timesum > self.ev_complete_time:
                is_intervention = True
                is_intervention_set = True
                self.intervention_phase_label = label
                intervention_index = i
            if is_eta_set == False and timesum > self.ev_eta:
                is_eta = True
                is_eta_set = True
                eta_index = i
            phase_overview = [label, time, is_intervention, is_eta]
            sequence_segments.append(phase_overview)

        sequence_overview['segments'] = sequence_segments
        sequence_overview['intervention_index'] = intervention_index
        sequence_overview['eta_index'] = eta_index
        self.intervention_cycle_sequence_overview = sequence_overview


    ######################################################
    ###################### GETTERS #######################
    ######################################################


    def get_incident_id(self):
        return self.incident_id

    def get_intervention_main_row(self):
        return self.intervention_main_row

    def get_incident_main_rows(self):
        return self.incident_main_rows

    def get_intervention_main_row_index(self):
        return self.intervention_main_row_index

    def get_intervention_phase_label(self):
        return self.intervention_phase_label

    def get_incident_detail_rows(self):
        return self.incident_detail_rows

    def get_intervention_cycle_start(self):
        return self.intervention_cycle_start

    def get_incident_cycle_interval(self):
        return self.incident_cycle_interval

    def get_incident_cycle_interval_phase_sums(self):
        return self.incident_cycle_interval_phase_sums

    def get_incident_cycle_phase_durations(self):
        return self.incident_cycle_phase_durations

    def get_incident_cycle_phase_labels(self):
        return self.incident_cycle_phase_labels

    def get_incident_cycle_timecomp(self):
        return self.incident_cycle_timecomp

    def get_NO_CYCLE_INTERVALS(self):
        return self.NO_CYCLE_INTERVALS

    def get_is_complete(self):
        return self.is_complete

    def get_ev_accepted(self):
        return self.ev_accepted

    def get_ev_eta(self):
        return self.ev_eta

    def get_ev_running(self):
        return self.ev_running

    def get_ev_cancelled(self):
        return self.ev_cancelled

    def get_ev_terminated(self):
        return self.ev_terminated

    def get_ev_complete_time(self):
        return self.ev_complete_time

    def get_ev_complete_time_state(self):
        return self.ev_complete_time_state

    def get_ev_status_datetimes(self):
        return self.ev_status_datetimes

    def get_cycle_phase_values(self, row):
        # Prep vals for pie chart
        labels_pre = ["1A","1B","1C","1D","1E","1F","2A","2B","2C","2D","2E","2F"]
        check_vals = ["1A","1B","1C","1D","1E","1F","2A","2B","2C","2D","2E","2F"]
        phases_pre = []
        for i in range(0, len(check_vals)):
            if check_vals[i] not in row.index.values.tolist():
                labels_pre.remove(check_vals[i])
            else:
                phases_pre.append(row[check_vals[i]])
        # Remove null values]
        labels = []
        phases = []
        for i in range(len(labels_pre)):
            if not np.isnan(phases_pre[i]):
                labels.append(labels_pre[i])
                phases.append(phases_pre[i])
        if (len(labels) == 0) or (len(phases) == 0):
            # print("Error: Zero phases fetched from dataframe - get_cycle_phase_values")
            raise ValueError('Zero phases fetched from dataframe - get_cycle_phase_values.')
        # Sort in right order
        order = list(row["Phase Combo"])
        label_count = [False for x in labels]
        labels_ordered = []
        phases_ordered = []
        for phase in order:
            index_in_labels = labels.index("1" + phase)
            if label_count[index_in_labels] == True:
                labels_ordered.append(labels[labels.index("2" + phase)])
                phases_ordered.append(phases[labels.index("2" + phase)])
            else:
                labels_ordered.append(labels[index_in_labels])
                phases_ordered.append(phases[index_in_labels])
                label_count[index_in_labels] = True
        return (labels_ordered, phases_ordered)

    def get_closest_datetime(self, i_datetime, df):
        # Input: (specified date, relating main dataframe)
        # Create time interval of 10 sec
        before = i_datetime - pd.Timedelta(minutes=10)
        after = i_datetime + pd.Timedelta(minutes=10)
        rows = df[df["Time"] > before]
        rows = rows[rows["Time"] < after]
        rows = rows.sort_values(by="Time")

        if rows.shape[0] == 0:
            return (False, False)

        # Set starting point for loop as the first rows' datetime
        current_datetime = rows.iloc[0]["Time"]
        current_datetime_index = 0

        # Iterate through to find closest (floor) datetime]
        for index, row in rows.iterrows():
            row_datetime = row["Time"]
            row_index = index
            # If later than i_datetime stop loop
            if row_datetime > i_datetime:
                break
            # If less or the same, save for later
            current_datetime = row_datetime
            current_datetime_index = index

        return (current_datetime, current_datetime_index)

    def get_intersection_validation(self, i_vpp, i_io, VALIDATION_WORKBOOK, VALIDATION_WORKBOOK_INDEX):
        date_format = VALIDATION_WORKBOOK.add_format({"num_format": "dd/mm/yy hh:mm:ss"})
        VALIDATION_WORKSHEET = VALIDATION_WORKBOOK.get_worksheet_by_name('VALIDATION')
        has_anomaly = False
        eta = self.ev_eta
        # print("eta: ", eta)
        flush_time = None
        queue_flush_time = None
        vehicle_clearance_time = None
        eti = None
        minumum_green = None
        amber = None
        red = None
        vehicle_safety_minimum = None
        last_phase_calltime = None
        pedestian_clearance = None
        earliest_time = None

        # Queue flush start: ETA - Flush time
        flush_time = i_vpp[i_vpp["Flush_Time"] > 0].iloc[0]["Flush_Time"]
        # print("flush_time: ", flush_time)
        queue_flush_time = eta - pd.Timedelta(seconds=flush_time)
        # print("queue_flush_time: ", queue_flush_time)

        # ETI: ETA - Flush Time - Clearance time
        # ETI: Queue Flush Time - Clearance time
        vehicle_clearance_time = i_vpp[i_vpp["Vehicle_Clearance_Time"] > 0].iloc[0]["Vehicle_Clearance_Time"]
        # print("vehicle_clearance_time: ", vehicle_clearance_time+flush_time)
        eti = queue_flush_time - pd.Timedelta(seconds=vehicle_clearance_time)
        # print("eti: ", eti)

        # Vehicle Safety Minimum: Minimum Green + Amber + Red
        intervention_phase = list(self.intervention_phase_label)[1]
        minimum_green = i_io.iloc[0]["Minimum_Green_" + intervention_phase]
        amber = i_io.iloc[0]["Amber_" + intervention_phase]
        red = i_io.iloc[0]["Red_" + intervention_phase]
        vehicle_safety_minimum = minimum_green + amber + red
        # print("vehicle_safety_minimum: ", vehicle_safety_minimum+vehicle_clearance_time+flush_time)

        # Last Phase Calltime: ETA - Flush Time - Clearance Time - Vehicle Safety Minimum
        # Last Phase Calltime: ETI - Vehicle Safety Minimum
        last_phase_calltime = eti - pd.Timedelta(seconds=vehicle_safety_minimum)
        # print("last_phase_calltime: ", last_phase_calltime)

        # Pedestian Clearance
        i_row = self.intervention_main_row
        ped_combo = i_row["Ped Combo"]
        is_ped_walk = False
        if ped_combo != "None":
            pwalk_run = True
            is_ped_walk = True
            pwalk_run_i = 1
            pwalk_high_current = 0
            pwalk_high_i = 0
            while pwalk_run:
                #if not np.isnan(phases_pre[i]):
                pwalk_label = "1P" + str(pwalk_run_i) + "WALK"
                if pwalk_label in i_row.keys():
                    pwalk_val = i_row[pwalk_label]
                    if pwalk_val > pwalk_high_current:
                        pwalk_high_current = pwalk_val
                        pwalk_high_i = pwalk_run_i
                else:
                    pwalk_run = False

                pwalk_run_i += 1

            pedestian_clearance = i_io.iloc[0]["Clearance_" + str(pwalk_high_i)]
        else:
            pedestian_clearance = 0
        # print("pedestian_clearance: ", pedestian_clearance+vehicle_clearance_time+flush_time)

        # Earliest Time: ETA - Flush Time - Clearance Time - Vehicle Safety Minimum - Pedestian Clearance
        # Earliest Time: Last Phase Calltime - Pedestian Clearance
        earliest_time = eti - pd.Timedelta(seconds=pedestian_clearance)
        # print("earliest_time: ", earliest_time)


        #=======================================================#
        ###################### VALIDATION #######################
        #=======================================================#


        # Validation - Last time intervention phase will be green (D)
        # If intervention phase start time is later than queue flush time: Faulty
        intervention_start = self.intervention_cycle_sequence_overview['segments'][self.intervention_cycle_sequence_overview['intervention_index']][1]
        intervention_label = self.intervention_cycle_sequence_overview['segments'][self.intervention_cycle_sequence_overview['intervention_index']][0]
        if queue_flush_time < intervention_start:
            diff = (intervention_start - queue_flush_time).total_seconds()
            # print('======= BREAKS: Intervention phase {} starts {} s after queue flush time ({})'.format(intervention_label, diff, queue_flush_time))
            VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 0, self.incident_id)
            VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 1, self.intervention_main_row["Time"], date_format)
            VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 2, 'D')
            VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 3, 'Intervention phase {} starts {} s after queue flush time ({})'.format(intervention_label, diff, queue_flush_time))
            VALIDATION_WORKBOOK_INDEX += 1
            has_anomaly = True


        # Validattion - Last time a new phase can be called (B)
        # Get eta and last phase calltime
        # If phase start times occur between eta and last phase calltime: Faulty
        eta_index = self.intervention_cycle_sequence_overview['eta_index']
        segments = self.intervention_cycle_sequence_overview['segments'][0:eta_index]
        segments = segments[::-1]

        for segment in segments:
            segment_start = segment[1]
            diff = (segment_start - last_phase_calltime).total_seconds()
            if diff >= 1:
                # print('======= BREAKS: {} starts {} s after last phase call time ({})'.format(segment[0], diff, last_phase_calltime))
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 0, self.incident_id)
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 1, self.intervention_main_row["Time"], date_format)
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 2, 'B')
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 3, '{} starts {} s after last phase call time ({})'.format(segment[0], diff, last_phase_calltime))
                VALIDATION_WORKBOOK_INDEX += 1


        # Validation - Earliest time an intervention will commence (A)
        # earliest_time > intervention_start: Fault
        # NOTE: Give notice if timestamp is earlier than 6AM, might be caused due to few and longer phases
        if (is_ped_walk == True) and (earliest_time > intervention_start):
            # Before 6AM?
            diff = (earliest_time - intervention_start).total_seconds()
            early_hour = intervention_start.replace(hour=7, minute=0, second=0)
            # print("early_hour: ", early_hour)
            if intervention_start < early_hour:
                # print('======= BREAKS: Intervention phase {} is called {} s before earliest time intervention phase should commence ({}). Timestamp is earlier than 7AM which cause less and longer phases.'.format(intervention_label, diff, earliest_time))
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 0, self.incident_id)
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 1, self.intervention_main_row["Time"], date_format)
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 2, 'A')
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 3, 'Intervention phase {} is called {} s before earliest time intervention phase should commence ({}). Timestamp is earlier than 7AM which cause less and longer phases.'.format(intervention_label, diff, earliest_time))
                VALIDATION_WORKBOOK_INDEX += 1
            else:
                # print('======= BREAKS: Intervention phase {} is called {} s before earliest time intervention phase should commence ({})'.format(intervention_label, diff, earliest_time))
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 0, self.incident_id)
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 1, self.intervention_main_row["Time"], date_format)
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 2, 'A')
                VALIDATION_WORKSHEET.write(VALIDATION_WORKBOOK_INDEX, 3, 'Intervention phase {} is called {} s before earliest time intervention phase should commence ({})'.format(intervention_label, diff, earliest_time))
                VALIDATION_WORKBOOK_INDEX += 1

        return (VALIDATION_WORKBOOK, VALIDATION_WORKBOOK_INDEX)



    def to_string(self):
        print("incident_id: ", incident_id)
        print("intervention_main_row: ", intervention_main_row)
        print("incident_main_rows: ", incident_main_rows)
        print("intervention_main_row_index: ", intervention_main_row_index)
        print("intervention_phase_label: ", intervention_phase_label)
        print("incident_detail_rows: ", incident_detail_rows)
        print("intervention_cycle_start: ", intervention_cycle_start)
        print("incident_cycle_interval: ", incident_cycle_interval)
        print("incident_cycle_interval_phase_sums: ", incident_cycle_interval_phase_sums)
        print("incident_cycle_phase_durations: ", incident_cycle_phase_durations)
        print("incident_cycle_phase_labels: ", incident_cycle_phase_labels)
        print("incident_cycle_timecomp: ", incident_cycle_timecomp)
        print("NO_CYCLE_INTERVALS: ", NO_CYCLE_INTERVALS)
        print("is_complete: ", is_complete)
        print("ev_accepted: ", ev_accepted)
        print("ev_eta: ", ev_eta)
        print("ev_running: ", ev_running)
        print("ev_cancelled: ", ev_cancelled)
        print("ev_terminated: ", ev_terminated)
        print("ev_complete_time: ", ev_complete_time)
        print("ev_complete_time_state: ", ev_complete_time_state)
        print("ev_status_datetimes: ", ev_status_datetimes)
