# Python modules
from __future__ import division

# 3rd party modules


# Our modules
import vespa.common.util.db as common_util_db
from vespa.common.util.db import _Fetch
import vespa.common.rfp_machine_settings as rfp_machine_settings
import vespa.common.constants as constants




class Database(common_util_db.Database):
    """A database class that looks and works just like 
    vespa.common.util.db.Database. This exists to provide methods that are 
    specific to RFPulse.
    """
    def __init__(self, filename):
        common_util_db.Database.__init__(self, filename)


    def delete_pulse_project(self, pulse_project_id, use_transactions=True):
        """Delete the pulse_project with the given pulse_project_id."""
        
        if use_transactions:
            self.begin_transaction()
            
        sql = """SELECT
                    *
                 FROM
                    pulse_projects
                 WHERE
                    id = ?
              """
        row = self._execute(sql, pulse_project_id, fetch=_Fetch.ONE)
  
        self._delete_master_parameters(row["master_parameters_id"])
        self.delete_machine_settings(row["machine_settings_id"]) 

        sql = """SELECT
                    *
                 FROM
                    transformations
                 WHERE
                    pulse_project_id = ?
              """
        rows = self._execute(sql, (pulse_project_id), fetch=_Fetch.ALL)
              
        for row in rows:
            trans_type = constants.TransformationType.get_type_for_value(row["transformation_type"], 'db')
            self._delete_parameters(row["parameters_id"], trans_type)
            self._delete_result(row["result_id"])
              
        # Delete Transformations
        sql = """DELETE FROM
                    transformations
                 WHERE
                    pulse_project_id = ?
              """
        self._execute(sql, (pulse_project_id), fetch=_Fetch.NONE)

        sql = """DELETE FROM
                    pulse_projects
                 WHERE
                    id = ?
               """                       
        self._execute(sql, pulse_project_id, _Fetch.NONE)

        if use_transactions:
            self.commit()
    
    
    def delete_pulse_projects(self, pulse_project_ids):
        self.begin_transaction()
        for ppid in pulse_project_ids:
            self.delete_pulse_project(ppid, False)
        self.commit()


    def replace_pulse_project(self, pulse_project, results_to_skip=[ ]):
        """
        Deletes and re-inserts a pulse_project with the same UUID. 
        The pulse project must exist in the database.

        This is as close as we get to update_pulse_project().

        See insert_pulse_project() for an explanation of results_to_skip
        """
        
        self.begin_transaction()

        assert(self.exists_pulse_project_in_database(pulse_project.id))
        
        self.delete_pulse_project(pulse_project.id, False)

        self.insert_pulse_project(pulse_project, False, results_to_skip)
        
        self.commit()


    def delete_transform_kernels(self, transform_kernel_ids):
        """Given a single transform_kernel id or a list of them, deletes the 
        transform_kernel(s) and associated params. 
        
        If any of the pulse sequences are in use by experiments, the deletion
        will fail. 
        """
        if isinstance(transform_kernel_ids, basestring):
            transform_kernel_ids = [transform_kernel_ids]
                
        for id_ in transform_kernel_ids:
            self.begin_transaction()
            
#             # Failsafe here -- transform_kernel_ids that are referenced by a 
#             # pulse_project must not be deleted and should never be passed to
#             # this function.
#             sql = """SELECT
#                         count(*)
#                      FROM
#                         pulse_projects
#                      WHERE
#                         transform_kernel_ids = ?"""
#             usage_count = self._execute(sql, id_, _Fetch.SINGLETON)
#             
#             assert(not usage_count)

            # Delete user_parameters, then the transform_kernel.
            sql = """DELETE FROM
                        transform_kernel_user_parameters
                     WHERE
                        transform_kernel_id = ?"""
            self._execute(sql, id_, _Fetch.NONE)

            sql = """DELETE FROM
                        transform_kernels
                     WHERE
                        id = ?
                   """
            self._execute(sql, id_, _Fetch.NONE)

            self.commit()


    def replace_transform_kernel(self, transform_kernel):
        """
        Deletes and re-inserts a transform_kernel with the same UUID. 
        The transform_kernel must exist in the database.

        This is as close as we get to update_transform_kernel().

        """
        self.begin_transaction()

        assert(self.exists_transform_kernel_in_database(transform_kernel.id))
        
        self.delete_transform_kernels(transform_kernel.id)

        self.insert_transform_kernel(transform_kernel)
        
        self.commit()
                 
        
    def update_machine_settings(self, machine_settings):
        
        """Saves the machine settings described by the input parameter. 
        The machine settings must already exist in the database.
        
        It doesn't matter if the machine settings object is a template or not.
        """
        # Templates are a little different from the settings associated with
        # a pulse project.
        is_template = isinstance(machine_settings,
                                 rfp_machine_settings.MachineSettingsTemplate)

        name = machine_settings.name if is_template else None
        is_default = machine_settings.is_default if is_template else False
        # I translate machine type to the correct constant, but only if it's
        # not freeform text.
        machine_type = machine_settings.machine_type
        if machine_type in constants.MachineType.ALL:
            machine_type = machine_type['db']
        
        sql = """UPDATE
                    machine_settings
                 SET
                    name = ?,
                    is_default = ?,
                    machine_type = ?, 
                    field_strength = ?, max_b1_field = ?,
                    zero_padding = ?, min_dwell_time = ?,
                    dwell_time_increment = ?, 
                    gradient_raster_time = ?,
                    gradient_slew_rate = ?,
                    gradient_maximum = ?
                 WHERE
                    id = ?
              """
        
        sql_params = (name, is_default, machine_type,
                      machine_settings.field_strength,
                      machine_settings.max_b1_field,
                      machine_settings.zero_padding,
                      machine_settings.min_dwell_time,
                      machine_settings.dwell_time_increment,
                      machine_settings.gradient_raster_time,
                      machine_settings.gradient_slew_rate,
                      machine_settings.gradient_maximum,
                      machine_settings.id)

        self._execute(sql, sql_params, _Fetch.NONE)


    #################           Private  Methods           #################
    ##################   (in alphabetic order, no less!)   #################

    def _delete_master_parameters(self, master_parameters_id):

        if not master_parameters_id:
            return

        sql = """DELETE FROM
                    master_parameters
                 WHERE
                    id = ?
              """
        self._execute(sql, master_parameters_id, _Fetch.NONE)


    def _delete_gradient(self, gradient_id):
        # Currently this code is only called from within a transaction, so
        # it doesn't need to open a transaction itself.
        if not gradient_id:
            return

        sql = '''DELETE FROM
                    gradient_waveforms
                 WHERE
                    gradient_id = ?
              '''
                      
        self._execute(sql, gradient_id, fetch=_Fetch.NONE)           
                      
        sql = """DELETE FROM
                    gradients
                 WHERE
                    id = ?                                   
              """
        self._execute(sql, gradient_id, _Fetch.NONE)       


    def _delete_gaussian_parameters(self, parameters_id):
               
        sql = '''DELETE FROM
                    gaussian_pulse_parameters
                 WHERE
                    id = ?                        
              '''        
        self._execute(sql, parameters_id, _Fetch.NONE)  


    def _delete_hs_parameters(self, parameters_id):
               
        sql = '''DELETE FROM
                    hs_pulse_parameters
                 WHERE
                    id = ?                        
              '''        
        self._execute(sql, parameters_id, _Fetch.NONE)      
        

    def _delete_import_parameters(self, parameters_id):
               
        sql = '''DELETE FROM
                    import_pulse_parameters
                 WHERE
                    id = ?                        
              '''        
        self._execute(sql, parameters_id, _Fetch.NONE) 
    
    
    def _delete_interpolate_rescale_parameters(self, parameters_id):

        sql = """DELETE FROM
                    interpolate_rescale_parameters
                 WHERE
                    id = ?
              """

        self._execute(sql, parameters_id, _Fetch.NONE)


    def _delete_ocn_parameters(self, parameters_id):

        sql = """DELETE FROM
                    ocn_parameters
                 WHERE
                    id = ?
              """

        self._execute(sql, parameters_id, _Fetch.NONE)


    def _delete_ocn_state(self, ocn_state_id):
        
        if not ocn_state_id:
            return
 
        # Delete all the individual data points
        sql = '''DELETE FROM
                    deltab1_points
                 WHERE
                    ocn_state_id = ?
              '''          
        self._execute(sql, ocn_state_id, _Fetch.NONE)         
               
        # Delete the residual error history
        sql = '''DELETE FROM
                    ocn_residual_errors
                 WHERE
                    ocn_state_id = ?
              '''          
        self._execute(sql, ocn_state_id, _Fetch.NONE)

        # Delete the OC state itself
        sql = '''DELETE FROM
                    ocn_states
                 WHERE
                    id = ?                        
              '''        
        self._execute(sql, ocn_state_id, _Fetch.NONE)  


    def _delete_parameters(self, parameters_id, trans_type):

        if not parameters_id:
            return
        
        if trans_type == constants.TransformationType.CREATE_SLR:
            return self._delete_slr_parameters(parameters_id)

        elif trans_type == constants.TransformationType.CREATE_GAUSSIAN:
            return self._delete_gaussian_parameters(parameters_id) 
                    
        elif trans_type == constants.TransformationType.CREATE_RANDOMIZED:
            return self._delete_randomized_parameters(parameters_id) 

        elif trans_type == constants.TransformationType.CREATE_IMPORT:
            return self._delete_import_parameters(parameters_id) 
                            
        elif trans_type == constants.TransformationType.CREATE_HYPERBOLIC_SECANT:
            return self._delete_hs_parameters(parameters_id)        
        
        elif trans_type == constants.TransformationType.INTERPOLATE_RESCALE:
            return self._delete_interpolate_rescale_parameters(parameters_id)
                    
        elif trans_type == constants.TransformationType.OCN:
            return self._delete_ocn_parameters(parameters_id)
                    
        elif trans_type == constants.TransformationType.ROOT_REFLECTION:
            return self._delete_root_reflect_parameters(parameters_id)
                             
        else:
            error_string = "Unknown transformation/params type: Unable to delete."
            raise NotImplementedError(error_string)
    
    
    def _delete_randomized_parameters(self, id_):
               
        sql = '''DELETE FROM
                    randomized_pulse_parameters
                 WHERE
                    id = ?                        
              '''        
        self._execute(sql, id_, _Fetch.NONE)         


    def _delete_result(self, result_id):    
        # Currently this code is only called from within a transaction, so
        # it doesn't need to open a transaction itself.
        if not result_id:
            return
 
        sql = """SELECT
                    *
                 FROM
                    results
                 WHERE
                    id = ?
              """
        row = self._execute(sql, result_id, fetch=_Fetch.ONE) 
        
        self._delete_gradient(row["gradient_id"])
        self._delete_ocn_state(row["ocn_state_id"]) 
 
        # Now delete all the individual data points, 
        # from the rf_waveforms table, for this rfpulse.
        sql = '''DELETE FROM
                    rf_waveforms
                 WHERE
                    result_id = ?
              '''          
        self._execute(sql, result_id, _Fetch.NONE) 
            
        # Now delete the "container" table for this result.
        sql = '''DELETE FROM
                    results
                 WHERE
                    id = ?
              '''   
        self._execute(sql, result_id, _Fetch.NONE)    
    
    
    def _delete_root_reflect_parameters(self, parameters_id):
        
        sql = """DELETE FROM
                    root_reflect_parameters
                 WHERE
                    id = ?
              """
              
        self._execute(sql, parameters_id, _Fetch.NONE)
    
    
        sql = """DELETE FROM
                    a_roots
                 WHERE
                    root_reflect_id = ?
              """
              
        self._execute(sql, parameters_id, _Fetch.NONE)
    
    
        sql = """DELETE FROM
                    b_roots
                 WHERE
                    root_reflect_id = ?
              """

        self._execute(sql, parameters_id, _Fetch.NONE)    
    
    
    def _delete_slr_parameters(self, parameters_id):
               
        sql = '''DELETE FROM
                    slr_pulse_parameters
                 WHERE
                    id = ?                        
              '''        
        self._execute(sql, (parameters_id), _Fetch.NONE)         


