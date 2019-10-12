import sys
import dcs
import dcs.mission
import dcs.task
import dcs.mapping
import dcs.point
from dcs.mapping import Point, Polygon
import dcs.terrain
import dcs.unittype
import dcs.vehicles
import dcs.coalition
from dcs.countries import USA, Russia
import random
import datetime
import argparse
import os

red_control = Polygon([Point(-265942.85714286, 603885.71428571), Point(-233257.14285714, 632685.71428571),
                       Point(-175257.14285714, 642257.14285714), Point(-194257.14285714, 881257.14285715),
                       Point(-45114.285714285, 856971.42857143), Point(55457.142857144, 265257.14285715),
                       Point(-56542.857142856, 266114.28571429)])


def T72_brigade(mission, country, position, heading, name, skill=dcs.unit.Skill.Average):
    units = [dcs.vehicles.Armor.MBT_T_72B, dcs.vehicles.Armor.MBT_T_72B, dcs.vehicles.Armor.MBT_T_72B,
             dcs.vehicles.Armor.MBT_T_72B, dcs.vehicles.Armor.MBT_T_72B, dcs.vehicles.Armor.MBT_T_72B,
             dcs.vehicles.Armor.IFV_BMP_2, dcs.vehicles.Armor.IFV_BMP_2, dcs.vehicles.AirDefence.SPAAA_ZSU_23_4_Shilka,
             dcs.vehicles.AirDefence.SAM_SA_13_Strela_10M3_9A35M3, dcs.vehicles.Unarmed.Transport_Ural_4320_31_Armored]
    vg = mission.vehicle_group_platoon(
        country, name, units, position, heading)

    vg.formation_scattered(random.randint(0, 360))

    for u in vg.units:
        u.skill = skill

    return vg


def military_base(mission, country, position, name):
    base = []
    base.append(mission.static_group(country, name + " Command Center", dcs.statics.Fortification.Command_Center,
                                     position, 270))
    base.append(mission.static_group(country, name + " Ammo", dcs.statics.Fortification.FARP_Ammo_Storage,
                                     position.point_from_heading(0, 180)))
    base.append(mission.static_group(country, name + " Barracks 1", dcs.statics.Fortification.Barracks_2,
                position.point_from_heading(45, 50), 180))
    base.append(mission.static_group(country, name + " Barracks 2", dcs.statics.Fortification.Barracks_2,
                base[-1].position.point_from_heading(0, 20), 180))
    base.append(mission.static_group(country, name + " Barracks 3", dcs.statics.Fortification.Barracks_2,
                base[-1].position.point_from_heading(0, 20), 180))
    base.append(mission.static_group(country, name + " Barracks 4", dcs.statics.Fortification.Barracks_2,
                base[-1].position.point_from_heading(0, 20), 180))
    base.append(mission.static_group(country, name + " Barracks 5", dcs.statics.Fortification.Barracks_2,
                base[-1].position.point_from_heading(0, 20), 180))

    base.append(mission.static_group(country, name + " Bunker", dcs.statics.Fortification.Bunker,
                position.point_from_heading(315, 50), 270))
    base.append(mission.static_group(country, name + " Fuel depot", dcs.statics.Fortification.FARP_Fuel_Depot,
                base[-1].position.point_from_heading(0, 20), 270))
    base.append(mission.static_group(country, name + " Garage", dcs.statics.Fortification.Garage_A,
                base[-1].position.point_from_heading(0, 30)))
    base.append(mission.static_group(country, name + " Generator", dcs.statics.Fortification.GeneratorF,
                base[-1].position.point_from_heading(0, 20)))
    base.append(mission.static_group(country, name + " Cargo 1", dcs.statics.Cargo.ammo_cargo,
                base[-1].position.point_from_heading(0, 10)))
    base.append(mission.static_group(country, name + " Cargo 2", dcs.statics.Cargo.ammo_cargo,
                base[-1].position.point_from_heading(0, 10)))
    base.append(mission.static_group(country, name + " Cargo 3", dcs.statics.Cargo.iso_container,
                base[-1].position.point_from_heading(0, 10)))

    base.append(mission.static_group(country, name + " watch tower 1", dcs.statics.Fortification.TowerArmed,
                                     position.point_from_heading(90, 80)))
    base.append(mission.static_group(country, name + " watch tower 2", dcs.statics.Fortification.TowerArmed,
                                     base[-1].position.point_from_heading(0, 200)))
    base.append(mission.static_group(country, name + " watch tower 3", dcs.statics.Fortification.TowerArmed,
                                     position.point_from_heading(270, 80)))
    base.append(mission.static_group(country, name + " watch tower 4", dcs.statics.Fortification.TowerArmed,
                                     base[-1].position.point_from_heading(0, 200)))

    return base


class Campaign:
    FlyTypes = {**dcs.planes.plane_map, **dcs.helicopters.helicopter_map}
    Statics = {**dcs.statics.fortification_map, **dcs.statics.warehouse_map, **dcs.statics.cargo_map}

    def __init__(self):
        self.startdate = datetime.datetime(2017, 5, 24, 9, 12, 0, tzinfo=datetime.timezone.utc)
        self.time = 0
        self.d = {}
        self.baric_system = dcs.weather.Weather.BaricSystem.AntiCyclone

    def flyinggroup_data(self, g: dcs.unitgroup.FlyingGroup, country_id: int):
        d = {
            "name": str(g.name),
            "airport": g.airport_id(),
            "country": country_id,
            "units": []
        }

        for u in g.units:
            ud = {
                "name": str(u.name),
                "x": u.position.x,
                "y": u.position.y,
                "alt": u.alt,
                "type": u.type,
                "skill": u.skill.value,
                "livery": u.livery_id
            }
            if d["airport"]:
                ud["parking"] = u.parking
                ud["parking_id"] = u.parking_id
            d["units"].append(ud)
        return d

    def staticgroup_data(self, s: dcs.unitgroup.StaticGroup, country_id: int):
        d = {
            "name": str(s.name),
            "country": country_id,
            "type": s.units[0].type,
            "x": s.position.x,
            "y": s.position.y,
            "heading": s.heading
        }

        return d

    def scan_mission(self, m: dcs.mission.Mission):
        self.d = {
            "coalition": {
                "red": {
                    "planes": [],
                    "helicopters": [],
                    "statics": []
                },
                "blue": {
                    "planes": [],
                    "helicopters": [],
                    "statics": []
                },
            },
            "airports": {}
        }

        for a in m.terrain.airport_list():
            self.d["airports"][str(a.id)] = a.coalition.lower()

        for col in m.coalition:
            for cn in m.coalition[col].countries:
                c = m.country(cn)
                for pg in c.plane_group:
                    d = self.flyinggroup_data(pg, c.id)
                    d["processed"] = False
                    self.d["coalition"][col]["planes"].append(d)

                for pg in c.helicopter_group:
                    d = self.flyinggroup_data(pg, c.id)
                    d["processed"] = False
                    self.d["coalition"][col]["helicopters"].append(d)

                for sg in c.static_group:
                    d = self.staticgroup_data(sg, c.id)
                    d["processed"] = False
                    self.d["coalition"][col]["statics"].append(d)

    @staticmethod
    def is_awacs(type_id):
        return dcs.planes.plane_map[type_id].category == "AWACS"

    def apply_unit_values(self, m: dcs.mission.Mission, fg: dcs.unitgroup.FlyingGroup, dunits):
        for i in range(0, len(dunits)):
            fg.units[i].skill = dcs.unit.Skill(dunits[i]["skill"])
            fg.units[i].livery_id = dunits[i]["livery"]
            fg.units[i].name = m.string(dunits[i]["name"])

    def setup_awacs(self, m: dcs.mission.Mission):

        for coln in self.d["coalition"]:
            col = self.d["coalition"][coln]
            awacs = None
            print("COL", col)
            for pg in col["planes"]:
                if Campaign.is_awacs(pg["units"][0]["type"]):
                    airport = m.terrain.airport_by_id(pg["airport"])
                    counter_airport = m.terrain.nearest_airport(airport.position, "blue" if coln == 'red' else "red")
                    heading = airport.position.heading_between_point(counter_airport.position)
                    awacs = m.awacs_flight(
                        m.country_by_id(pg["country"]),
                        pg["name"],
                        dcs.planes.plane_map[pg["units"][0]["type"]],
                        airport,
                        airport.position.point_from_heading(heading + 180, 30 * 1000),
                        80 * 1000,
                        270)
                    self.apply_unit_values(m, awacs, pg["units"])
                    pg["processed"] = True
                    break

            if awacs:
                for pg in col["planes"]:
                    if pg["name"].lower().startswith("escort"):
                        airport = m.terrain.airport_by_id(pg["airport"])
                        ef = m.escort_flight(
                            m.country_by_id(pg["country"]),
                            pg["name"],
                            dcs.planes.plane_map[pg["units"][0]["type"]],
                            airport,
                            awacs,
                            group_size=len(pg["units"]))
                        self.apply_unit_values(m, ef, pg["units"])
                        pg["processed"] = True
                        break

    def setup_flights(self, m: dcs.mission.Mission):

        self.setup_awacs(m)
        russia = m.country("Russia")

        # cas flights
        cas_s = []  # type: List[dcs.unitgroup.FlyingGroup]
        targets = []
        for coln in self.d["coalition"]:
            col = self.d["coalition"][coln]
            for pg in col["planes"]:
                country = m.country_by_id(pg["country"])
                _type = dcs.planes.plane_map[pg["units"][0]["type"]]
                if _type.task_default == dcs.task.CAS and dcs.task.SEAD not in _type.tasks:
                    airport = m.terrain.airport_by_id(pg["airport"])
                    slots = []
                    for u in pg["units"]:
                        slots.append(airport.parking_slot(u["parking"]))
                    fg = m.flight_group_from_airport(country, pg["name"], _type, airport, dcs.task.CAS,
                                                     group_size=len(pg["units"]), parking_slots=slots)
                    cas_s.append(fg)
                    tgts = (russia.vehicle_group_within(airport.position, 115 * 1000) +
                            russia.static_group_within(airport.position, 115 * 1000))
                    tgts = [x for x in tgts if x.id not in targets]
                    target = random.choice(tgts)
                    targets.append(target)
                    m.strike_flight_to_group(fg, target)
                    self.apply_unit_values(m, cas_s[-1], pg["units"])
                    pg["processed"] = True

            for hg in col["helicopters"]:
                country = m.country_by_id(hg["country"])
                _type = dcs.helicopters.helicopter_map[hg["units"][0]["type"]]
                if _type.task_default == dcs.task.CAS:
                    airport = m.terrain.airport_by_id(hg["airport"])
                    slots = []
                    for u in hg["units"]:
                        slots.append(airport.parking_slot(u["parking"]))
                    fg = m.flight_group_from_airport(country, hg["name"], _type, airport, dcs.task.CAS,
                                                     group_size=len(hg["units"]), parking_slots=slots)
                    fg.add_runway_waypoint(airport)
                    cas_s.append(fg)
                    tgts = (russia.vehicle_group_within(airport.position, 60 * 1000) +
                            russia.static_group_within(airport.position, 60 * 1000))
                    tgts = [x for x in tgts if x.id not in targets]
                    target = random.choice(tgts)
                    targets.append(target)
                    m.strike_flight_to_group(fg, target)
                    self.apply_unit_values(m, cas_s[-1], hg["units"])
                    if not fg.has_human():
                        fg.delay_start(m, random.randrange(0, 60 * 60))
                    hg["processed"] = True

        # sead support
        available_seads = []
        for coln in self.d["coalition"]:
            col = self.d["coalition"][coln]
            for pg in col["planes"]:
                _type = dcs.planes.plane_map[pg["units"][0]["type"]]
                if dcs.task.SEAD in _type.tasks:
                    available_seads.append(pg)

        for cas in cas_s:
            if available_seads:
                sead = available_seads.pop()
                print("SEAD", sead)

                country = m.country_by_id(sead["country"])
                airport = m.terrain.airport_by_id(sead["airport"])
                _type = dcs.planes.plane_map[sead["units"][0]["type"]]
                slots = []
                for u in sead["units"]:
                    slots.append(airport.parking_slot(u["parking"]))
                fg = m.flight_group_from_airport(country, sead["name"], _type, airport, dcs.task.SEAD,
                                                 group_size=len(sead["units"]), parking_slots=slots)
                fg.add_runway_waypoint(airport)
                target_pos = cas.waypoint('Attack').position
                m.sead_flight_to_group(fg, target_pos)
                self.apply_unit_values(m, fg, sead["units"])
                sead["processed"] = True


        # place remaining flights
        for col in self.d["coalition"]:
            col = self.d["coalition"][col]
            for pg in [x for x in col["planes"] + col["helicopters"] if not x["processed"]]:
                print("REM", pg)
                if pg["airport"]:
                    _type = Campaign.FlyTypes[pg["units"][0]["type"]]
                    airport = m.terrain.airport_by_id(pg["airport"])
                    slots = [airport.parking_slot(x["parking"]) for x in pg["units"]]
                    f = m.flight_group_from_airport(
                        m.country_by_id(pg["country"]),
                        pg["name"],
                        _type,
                        airport, group_size=len(pg["units"]), parking_slots=slots)
                    f.add_runway_waypoint(airport)
                    f.uncontrolled = True
                    self.apply_unit_values(m, f, pg["units"])

                    pg["processed"] = True

    def setup_ground(self, m: dcs.mission.Mission):
        for col in self.d["coalition"]:
            col = self.d["coalition"][col]
            for sg in col["statics"]:
                country = m.country_by_id(sg["country"])
                if sg["type"] == dcs.statics.Fortification.Mark_Flag_Red.id:
                    military_base(m, country, dcs.mapping.Point(sg["x"], sg["y"]), sg["name"])
                else:
                    m.static_group(country, sg["name"],
                                   Campaign.Statics[sg["type"]], dcs.mapping.Point(sg["x"], sg["y"]),
                                   sg["heading"])

    def setup_mission(self, m: dcs.mission.Mission):
        m.start_time = self.startdate + datetime.timedelta(seconds=self.time)
        m.weather.dynamic_weather(self.baric_system, 2)

        for id, col in self.d["airports"].items():
            m.terrain.airport_by_id(int(id)).set_coalition(col)

        self.setup_flights(m)
        self.setup_ground(m)


def main():
    m = dcs.mission.Mission()
    nm = dcs.mission.Mission()
    m.load_file("C:\\Users\\peint\\Saved Games\\DCS\\Missions\\dcscs_setup\\warehouse.miz")

    mrussia = m.coalition["red"].country("Russia")
    musa = m.coalition["blue"].country("USA")

    russia = nm.country("Russia")
    usa = nm.country("USA")

    c = Campaign()
    c.scan_mission(m)
    redspawns = [z for z in m.triggers.zones() if z.name.startswith("red spawn")]
    print(redspawns)

    aaa_def = [[dcs.countries.Russia.Vehicle.AirDefence.AAA_ZU_23_Emplacement],
               [dcs.countries.Russia.Vehicle.AirDefence.SAM_SA_18_Igla_S_MANPADS,
                dcs.countries.Russia.Vehicle.AirDefence.SAM_SA_18_Igla_S_comm],
               [dcs.countries.Russia.Vehicle.AirDefence.SPAAA_ZSU_23_4_Shilka,
                dcs.countries.Russia.Vehicle.Armor.ARV_BRDM_2,
                dcs.countries.Russia.Vehicle.Armor.ARV_BRDM_2]]

    city_graph = nm.terrain.city_graph
    for spawn in redspawns:
        vg = T72_brigade(nm, russia, spawn.position, 0, spawn.name)
        near_node = city_graph.nearest_node(spawn.position)
        vg.add_waypoint(near_node.position, dcs.point.PointAction.OnRoad)
        city_graph.travel(vg, near_node, city_graph.node("Zugidi"))
        #vg.add_waypoint(city_graph.node("Zugidi").position, dcs.point.PointAction.OnRoad)

    for n in city_graph.rated_nodes_within(red_control, 60):
        r = random.random()
        if r > 0.9:
            dcs.templates.VehicleTemplate.sa11_site(nm, russia, n.position, random.randint(0, 360), n.name)
        elif r > 0.8:
            dcs.templates.VehicleTemplate.sa15_site(nm, russia, n.position, random.randint(0, 360), n.name)
        elif r > 0.2:
            nm.vehicle_group_platoon(
                russia,
                n.name + " def",
                random.choice(aaa_def),
                n.position.random_point_within(40, 20),
                random.randint(0, 360))

    zone = nm.triggers.add_triggerzone(dcs.mapping.Point(-247248, 618130), 5000, False, "intercept trigger")

    ig = nm.intercept_flight(russia, "fuck of", dcs.planes.Su_30, m.terrain.gudauta(), zone)

    c.setup_mission(nm)
    # awacs = m.awacs_flight(
    #     usa,
    #     "AWACS",
    #     plane_type=dcs.planes.E_3A,
    #     airport=m.terrain.vaziani(),
    #     position=m.terrain.vaziani().position.point_from_heading(200, 30 * 1000),
    #     race_distance=80 * 1000, heading=270,
    #     altitude=random.randrange(4000, 5500, 100), frequency=140)
    #
    # ef = m.escort_flight(usa, "AWACS Escort", dcs.countries.USA.Plane.M_2000C, m.terrain.vaziani(), awacs, group_size=2)
    # ef.delay_start(m, 180)


    nm.save("C:\\Users\\peint\\Saved Games\\DCS\\Missions\\fun.miz")
    return 0


if __name__ == '__main__':
    sys.exit(main())
