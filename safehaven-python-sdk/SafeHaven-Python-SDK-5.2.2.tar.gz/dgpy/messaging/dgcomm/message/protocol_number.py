#
# Syntropy legacy message protocol numbers
#
from enum import unique, IntEnum

@unique
class ProtoNum(IntEnum):
    """Protonum enumerates Syntropy protocol numbers, with custom attributes."""

    MSG_UI_CMS_USER_CREATE                                   = 3000
    MSG_UI_CMS_CREATE_DVOL                                   = 3001
    MSG_UI_CMS_EMAIL_CONFIG                                  = 3005
    MSG_UI_CMS_CREATE_PLUN                                   = 3006
    MSG_UI_CMS_DELETE_PLUN                                   = 3007
    MSG_UI_CMS_RESIZE_PLUN                                   = 3008
    MSG_UI_CMS_MIGRATE_DVOL                                  = 3009
    MSG_UI_CMS_EMAIL_CONFIG_LIST                             = 3011
    MSG_UI_CMS_SYNTROPY_SERVICE_START                        = 3013
    MSG_UI_CMS_LICENSE_ADD                                   = 3015
    MSG_UI_CMS_LICENSE_LIST                                  = 3016
    MSG_UI_CMS_DVOL_LIST_PLUN                                = 3017
    MSG_UI_CMS_DVOL_LIST_RECOVERY_PLAN                       = 3018
    MSG_UI_CMS_DVOL_CREATE_UPDATE_RECOVERY_PLAN              = 3019
    MSG_UI_CMS_USER_DELETE                                   = 3022
    MSG_UI_CMS_NODE_ADD                                      = 3029
    MSG_UI_CMS_NODE_DEL                                      = 3030
    MSG_UI_CMS_DVOL_DELETE                                   = 3031
    MSG_UI_CMS_DVOL_FAILOVER                                 = 3032
    MSG_UI_CMS_DVOL_FAILBACK_MS                              = 3033
    MSG_UI_CMS_DVOL_MANUAL_SNAPSHOT                          = 3034
    MSG_UI_CMS_DVOL_ROLLBACK                                 = 3035
    MSG_UI_CMS_LIST_DVOL_SNAP                                = 3036
    MSG_UI_CMS_DVOL_SET_SNAPSHOT_PERIOD                      = 3037
    MSG_UI_CMS_DVOL_CREATE_BACKUP_IMAGE                      = 3038
    MSG_UI_CMS_SYNTROPY_SERVICE_STOP                         = 3039
    MSG_UI_CMS_CMS_LIST                                      = 3040
    MSG_UI_CMS_DVOL_TEST_FAILOVER_DELETE_RS                  = 3041
    MSG_UI_CMS_DISK_CLAIM                                    = 3042
    MSG_UI_CMS_USER_LIST                                     = 3044
    MSG_UI_CMS_USER_SET_PASSWORD                             = 3045
    MSG_UI_CMS_DVOL_STORAGE_REPAIR                           = 3049
    MSG_UI_CMS_DVOL_UPDATE_STUB                              = 3068
    MSG_UI_CMS_DVOL_CONVERT_COW_TO_ROW                       = 3069
    MSG_UI_CMS_DVOL_DELETE_TARGET                            = 3070
    MSG_UI_CMS_DVOL_LIST_TARGETS                             = 3072
    MSG_UI_CMS_DVOL_SET_WAN_THROTTLE                         = 3073
    MSG_UI_CMS_DVOL_CONVERT_ROW_TO_COW                       = 3074
    MSG_UI_CMS_GET_BUILD_VERSION                             = 3075
    MSG_UI_CMS_ADD_PEER_SRN                                  = 3076
    MSG_UI_CMS_LIST_PEER_SRN                                 = 3077
    MSG_UI_CMS_DISK_UNCLAIM                                  = 3079
    MSG_UI_CMS_REMOVE_PEER_SRN                               = 3080
    MSG_UI_CMS_DVOL_RESIZE_ROW_POOL                          = 3082
    MSG_UI_CMS_DVOL_RESIZE_COW_POOL                          = 3084
    MSG_UI_CMS_DVOL_RESIZE_PRIMARY                           = 3085
    MSG_UI_CMS_DVOL_INSTALL_LRA                              = 3086
    MSG_UI_CMS_DVOL_INSTALL_MAKESTUB                         = 3087
    MSG_UI_CMS_DVOL_CONVERT_OOB                              = 3088
    MSG_UI_CMS_DVOL_ADD_VM                                   = 3089
    MSG_UI_CMS_DVOL_SCHEDULE_SNAPSHOT                        = 3090
    MSG_CMS_UI_USER_CREATE_SUC                               = 4000
    MSG_CMS_UI_CREATE_DVOL_SUC                               = 4001
    MSG_CMS_UI_EMAIL_CONFIG_SUC                              = 4005
    MSG_CMS_UI_CREATE_PLUN_SUC                               = 4006
    MSG_CMS_UI_DELETE_PLUN_SUC                               = 4007
    MSG_CMS_UI_RESIZE_PLUN_SUC                               = 4008
    MSG_CMS_UI_MIGRATE_DVOL_SUC                              = 4009
    MSG_CMS_UI_EMAIL_CONFIG_LIST_SUC                         = 4011
    MSG_CMS_UI_SYNTROPY_SERVICE_START_SUC                    = 4013
    MSG_CMS_UI_LICENSE_ADD_SUC                               = 4015
    MSG_CMS_UI_LICENSE_LIST_SUC                              = 4016
    MSG_CMS_UI_DVOL_LIST_PLUN_SUC                            = 4017
    MSG_CMS_UI_DVOL_LIST_RECOVERY_PLAN_SUC                   = 4018
    MSG_CMS_UI_DVOL_CREATE_UPDATE_RECOVERY_PLAN_SUC          = 4019
    MSG_CMS_UI_USER_DELETE_SUC                               = 4022
    MSG_CMS_UI_NODE_ADD_SUC                                  = 4029
    MSG_CMS_UI_NODE_DEL_SUC                                  = 4030
    MSG_CMS_UI_DVOL_DELETE_SUC                               = 4031
    MSG_CMS_UI_DVOL_FAILOVER_SUC                             = 4032
    MSG_CMS_UI_DVOL_FAILBACK_MS_SUC                          = 4033
    MSG_CMS_UI_DVOL_MANUAL_SNAPSHOT_SUC                      = 4034
    MSG_CMS_UI_DVOL_ROLLBACK_SUC                             = 4035
    MSG_CMS_UI_LIST_DVOL_SNAP_SUC                            = 4036
    MSG_CMS_UI_DVOL_SET_SNAPSHOT_PERIOD_SUC                  = 4037
    MSG_CMS_UI_DVOL_CREATE_BACKUP_IMAGE_SUC                  = 4038
    MSG_CMS_UI_SYNTROPY_SERVICE_STOP_SUC                     = 4039
    MSG_CMS_UI_CMS_LIST_SUC                                  = 4040
    MSG_CMS_UI_DVOL_TEST_FAILOVER_DELETE_RS_SUC              = 4041
    MSG_CMS_UI_DISK_CLAIM_SUC                                = 4042
    MSG_CMS_UI_USER_LIST_SUC                                 = 4044
    MSG_CMS_UI_USER_SET_PASSWORD_SUC                         = 4045
    MSG_CMS_UI_DVOL_STORAGE_REPAIR_SUC                       = 4049
    MSG_CMS_UI_DVOL_UPDATE_STUB_SUC                          = 4068
    MSG_CMS_UI_DVOL_CONVERT_COW_TO_ROW_SUC                   = 4069
    MSG_CMS_UI_DVOL_DELETE_TARGET_SUC                        = 4070
    MSG_CMS_UI_DVOL_LIST_TARGETS_SUC                         = 4072
    MSG_CMS_UI_DVOL_SET_WAN_THROTTLE_SUC                     = 4073
    MSG_CMS_UI_DVOL_CONVERT_ROW_TO_COW_SUC                   = 4074
    MSG_CMS_UI_GET_BUILD_VERSION_SUC                         = 4075
    MSG_CMS_UI_ADD_PEER_SRN_SUC                              = 4076
    MSG_CMS_UI_LIST_PEER_SRN_SUC                             = 4077
    MSG_CMS_UI_DISK_UNCLAIM_SUC                              = 4079
    MSG_CMS_UI_REMOVE_PEER_SRN_SUC                           = 4080
    MSG_CMS_UI_DVOL_RESIZE_ROW_POOL_SUC                      = 4082
    MSG_CMS_UI_DVOL_RESIZE_COW_POOL_SUC                      = 4084
    MSG_CMS_UI_DVOL_RESIZE_PRIMARY_SUC                       = 4085
    MSG_CMS_UI_DVOL_INSTALL_LRA_SUC                          = 4086
    MSG_CMS_UI_DVOL_INSTALL_MAKESTUB_SUC                     = 4087
    MSG_CMS_UI_DVOL_CONVERT_OOB_SUC                          = 4088
    MSG_CMS_UI_DVOL_ADD_VM_SUC                               = 4089
    MSG_CMS_UI_DVOL_SCHEDULE_SNAPSHOT_SUC                    = 4090
    MSG_CMS_UI_USER_CREATE_ERR                               = 5000
    MSG_CMS_UI_CREATE_DVOL_ERR                               = 5001
    MSG_CMS_UI_EMAIL_CONFIG_ERR                              = 5005
    MSG_CMS_UI_CREATE_PLUN_ERR                               = 5006
    MSG_CMS_UI_DELETE_PLUN_ERR                               = 5007
    MSG_CMS_UI_RESIZE_PLUN_ERR                               = 5008
    MSG_CMS_UI_MIGRATE_DVOL_ERR                              = 5009
    MSG_CMS_UI_EMAIL_CONFIG_LIST_ERR                         = 5011
    MSG_CMS_UI_SYNTROPY_SERVICE_START_ERR                    = 5013
    MSG_CMS_UI_LICENSE_ADD_ERR                               = 5015
    MSG_CMS_UI_LICENSE_LIST_ERR                              = 5016
    MSG_CMS_UI_DVOL_LIST_PLUN_ERR                            = 5017
    MSG_CMS_UI_DVOL_LIST_RECOVERY_PLAN_ERR                   = 5018
    MSG_CMS_UI_DVOL_CREATE_UPDATE_RECOVERY_PLAN_ERR          = 5019
    MSG_CMS_UI_USER_DELETE_ERR                               = 5022
    MSG_CMS_UI_NODE_ADD_ERR                                  = 5029
    MSG_CMS_UI_NODE_DEL_ERR                                  = 5030
    MSG_CMS_UI_DVOL_DELETE_ERR                               = 5031
    MSG_CMS_UI_DVOL_FAILOVER_ERR                             = 5032
    MSG_CMS_UI_DVOL_FAILBACK_MS_ERR                          = 5033
    MSG_CMS_UI_DVOL_MANUAL_SNAPSHOT_ERR                      = 5034
    MSG_CMS_UI_DVOL_ROLLBACK_ERR                             = 5035
    MSG_CMS_UI_LIST_DVOL_SNAP_ERR                            = 5036
    MSG_CMS_UI_DVOL_SET_SNAPSHOT_PERIOD_ERR                  = 5037
    MSG_CMS_UI_DVOL_CREATE_BACKUP_IMAGE_ERR                  = 5038
    MSG_CMS_UI_SYNTROPY_SERVICE_STOP_ERR                     = 5039
    MSG_CMS_UI_CMS_LIST_ERR                                  = 5040
    MSG_CMS_UI_DVOL_TEST_FAILOVER_DELETE_RS_ERR              = 5041
    MSG_CMS_UI_DISK_CLAIM_ERR                                = 5042
    MSG_CMS_UI_USER_LIST_ERR                                 = 5044
    MSG_CMS_UI_USER_SET_PASSWORD_ERR                         = 5045
    MSG_CMS_UI_DVOL_STORAGE_REPAIR_ERR                       = 5049
    MSG_CMS_UI_DVOL_UPDATE_STUB_ERR                          = 5068
    MSG_CMS_UI_DVOL_CONVERT_COW_TO_ROW_ERR                   = 5069
    MSG_CMS_UI_DVOL_DELETE_TARGET_ERR                        = 5070
    MSG_CMS_UI_DVOL_LIST_TARGETS_ERR                         = 5072
    MSG_CMS_UI_DVOL_SET_WAN_THROTTLE_ERR                     = 5073
    MSG_CMS_UI_DVOL_CONVERT_ROW_TO_COW_ERR                   = 5074
    MSG_CMS_UI_GET_BUILD_VERSION_ERR                         = 5075
    MSG_CMS_UI_ADD_PEER_SRN_ERR                              = 5076
    MSG_CMS_UI_LIST_PEER_SRN_ERR                             = 5077
    MSG_CMS_UI_DISK_UNCLAIM_ERR                              = 5079
    MSG_CMS_UI_REMOVE_PEER_SRN_ERR                           = 5080
    MSG_CMS_UI_DVOL_RESIZE_ROW_POOL_ERR                      = 5082
    MSG_CMS_UI_DVOL_RESIZE_COW_POOL_ERR                      = 5084
    MSG_CMS_UI_DVOL_RESIZE_PRIMARY_ERR                       = 5085
    MSG_CMS_UI_DVOL_INSTALL_LRA_ERR                          = 5086
    MSG_CMS_UI_DVOL_INSTALL_MAKESTUB_ERR                     = 5087
    MSG_CMS_UI_DVOL_CONVERT_OOB_ERR                          = 5088
    MSG_CMS_UI_DVOL_ADD_VM_ERR                               = 5089
    MSG_CMS_UI_DVOL_SCHEDULE_SNAPSHOT_ERR                    = 5090
    MSG_CMS_SER_CREATE_DVOL                                  = 6001
    MSG_CMS_SER_LIST_DVOL_PROP                               = 6002
    MSG_CMS_SER_DVOL_CONVERT_COW_TO_ROW                      = 6004
    MSG_CMS_SER_DVOL_CONVERT_ROW_TO_COW                      = 6005
    MSG_CMS_SER_MIGRATE_DVOL                                 = 6013
    MSG_CMS_SER_DVOL_SET_RESYNC_PERIOD                       = 6028
    MSG_CMS_SER_DVOL_DELETE                                  = 6032
    MSG_CMS_SER_DVOL_FAILOVER                                = 6033
    MSG_CMS_SER_DVOL_FAILBACK_MS                             = 6034
    MSG_CMS_SER_DVOL_FAILBACK_STOP_OLD_MASTER                = 6035
    MSG_CMS_SER_NODE_DEL                                     = 6038
    MSG_CMS_SER_DVOL_MANUAL_SNAPSHOT                         = 6039
    MSG_CMS_SER_DVOL_ROLLBACK                                = 6040
    MSG_CMS_SER_LIST_DVOL_SNAP                               = 6041
    MSG_CMS_SER_DVOL_SET_SNAPSHOT_PERIOD                     = 6043
    MSG_CMS_SER_DVOL_CREATE_BACKUP_IMAGE                     = 6044
    MSG_CMS_SER_UPDATE_CMS                                   = 6048
    MSG_CMS_SER_DVOL_TEST_FAILOVER_DELETE_RS                 = 6051
    MSG_CMS_SER_DISK_CLAIM                                   = 6053
    MSG_CMS_SER_DVOL_STORAGE_REPAIR                          = 6067
    MSG_CMS_SER_CREATE_PLUN                                  = 6079
    MSG_CMS_SER_DELETE_PLUN                                  = 6080
    MSG_CMS_SER_RESIZE_PLUN                                  = 6081
    MSG_CMS_SER_DVOL_LIST_PLUN                               = 6082
    MSG_CMS_SER_DVOL_ADD_TARGET                              = 6085
    MSG_CMS_SER_DVOL_DELETE_TARGET                           = 6086
    MSG_CMS_SER_DVOL_LIST_RECOVERY_PLAN                      = 6088
    MSG_CMS_SER_DVOL_CREATE_UPDATE_RECOVERY_PLAN             = 6089
    MSG_CMS_SER_DVOL_UPDATE_STUB                             = 6090
    MSG_CMS_SER_DVOL_LIST_TARGETS                            = 6091
    MSG_CMS_SER_DVOL_SET_WAN_THROTTLE                        = 6093
    MSG_CMS_SER_DISK_UNCLAIM                                 = 6095
    MSG_CMS_SER_DVOL_RESIZE_ROW_POOL                         = 6096
    MSG_CMS_SER_DVOL_RESIZE_COW_POOL                         = 6097
    MSG_CMS_SER_DVOL_RESIZE_PRIMARY                          = 6098
    MSG_CMS_SER_DVOL_INSTALL_LRA                             = 6099
    MSG_CMS_SER_DVOL_INSTALL_MAKESTUB                        = 6100
    MSG_CMS_SER_DVOL_CONVERT_OOB                             = 6101
    MSG_CMS_SER_SRN_ADD_PEER_SRN                             = 6102
    MSG_CMS_SER_SRN_REMOVE_PEER_SRN                          = 6103
    MSG_CMS_SER_DVOL_ADD_VM                                  = 6104
    MSG_CMS_SER_DVOL_SCHEDULE_SNAPSHOT                       = 6105
    MSG_SER_CMS_CREATE_DVOL_SUC                              = 7001
    MSG_SER_CMS_LIST_DVOL_PROP_SUC                           = 7002
    MSG_SER_CMS_DVOL_CONVERT_COW_TO_ROW_SUC                  = 7004
    MSG_SER_CMS_DVOL_CONVERT_ROW_TO_COW_SUC                  = 7005
    MSG_SER_CMS_MIGRATE_DVOL_SUC                             = 7013
    MSG_SER_CMS_DVOL_SET_RESYNC_PERIOD_SUC                   = 7028
    MSG_SER_CMS_DVOL_DELETE_SUC                              = 7032
    MSG_SER_CMS_DVOL_FAILOVER_SUC                            = 7033
    MSG_SER_CMS_DVOL_FAILBACK_MS_SUC                         = 7034
    MSG_SER_CMS_DVOL_FAILBACK_STOP_OLD_MASTER_SUC            = 7035
    MSG_SER_CMS_NODE_DEL_SUC                                 = 7038
    MSG_SER_CMS_DVOL_MANUAL_SNAPSHOT_SUC                     = 7039
    MSG_SER_CMS_DVOL_ROLLBACK_SUC                            = 7040
    MSG_SER_CMS_LIST_DVOL_SNAP_SUC                           = 7041
    MSG_SER_CMS_DVOL_SET_SNAPSHOT_PERIOD_SUC                 = 7043
    MSG_SER_CMS_DVOL_CREATE_BACKUP_IMAGE_SUC                 = 7044
    MSG_SER_CMS_UPDATE_CMS_SUC                               = 7048
    MSG_SER_CMS_DVOL_TEST_FAILOVER_DELETE_RS_SUC             = 7051
    MSG_SER_CMS_DISK_CLAIM_SUC                               = 7053
    MSG_SER_CMS_DVOL_STORAGE_REPAIR_SUC                      = 7067
    MSG_SER_CMS_CREATE_PLUN_SUC                              = 7079
    MSG_SER_CMS_DELETE_PLUN_SUC                              = 7080
    MSG_SER_CMS_RESIZE_PLUN_SUC                              = 7081
    MSG_SER_CMS_DVOL_LIST_PLUN_SUC                           = 7082
    MSG_SER_CMS_DVOL_ADD_TARGET_SUC                          = 7085
    MSG_SER_CMS_DVOL_DELETE_TARGET_SUC                       = 7086
    MSG_SER_CMS_DVOL_LIST_RECOVERY_PLAN_SUC                  = 7088
    MSG_SER_CMS_DVOL_CREATE_UPDATE_RECOVERY_PLAN_SUC         = 7089
    MSG_SER_CMS_DVOL_UPDATE_STUB_SUC                         = 7090
    MSG_SER_CMS_DVOL_LIST_TARGETS_SUC                        = 7091
    MSG_SER_CMS_DVOL_SET_WAN_THROTTLE_SUC                    = 7093
    MSG_SER_CMS_DISK_UNCLAIM_SUC                             = 7095
    MSG_SER_CMS_DVOL_RESIZE_ROW_POOL_SUC                     = 7096
    MSG_SER_CMS_DVOL_RESIZE_COW_POOL_SUC                     = 7097
    MSG_SER_CMS_DVOL_RESIZE_PRIMARY_SUC                      = 7098
    MSG_SER_CMS_DVOL_INSTALL_LRA_SUC                         = 7099
    MSG_SER_CMS_DVOL_INSTALL_MAKESTUB_SUC                    = 7100
    MSG_SER_CMS_DVOL_CONVERT_OOB_SUC                         = 7101
    MSG_SER_CMS_SRN_ADD_PEER_SRN_SUC                         = 7102
    MSG_SER_CMS_SRN_REMOVE_PEER_SRN_SUC                      = 7103
    MSG_SER_CMS_DVOL_ADD_VM_SUC                              = 7104
    MSG_SER_CMS_DVOL_SCHEDULE_SNAPSHOT_SUC                   = 7105
    MSG_SER_CMS_CREATE_DVOL_ERR                              = 8001
    MSG_SER_CMS_LIST_DVOL_PROP_ERR                           = 8002
    MSG_SER_CMS_DVOL_CONVERT_COW_TO_ROW_ERR                  = 8004
    MSG_SER_CMS_DVOL_CONVERT_ROW_TO_COW_ERR                  = 8005
    MSG_SER_CMS_MIGRATE_DVOL_ERR                             = 8013
    MSG_SER_CMS_DVOL_SET_RESYNC_PERIOD_ERR                   = 8028
    MSG_SER_CMS_DVOL_DELETE_ERR                              = 8032
    MSG_SER_CMS_DVOL_FAILOVER_ERR                            = 8033
    MSG_SER_CMS_DVOL_FAILBACK_MS_ERR                         = 8034
    MSG_SER_CMS_DVOL_FAILBACK_STOP_OLD_MASTER_ERR            = 8035
    MSG_SER_CMS_NODE_DEL_ERR                                 = 8038
    MSG_SER_CMS_DVOL_MANUAL_SNAPSHOT_ERR                     = 8039
    MSG_SER_CMS_DVOL_ROLLBACK_ERR                            = 8040
    MSG_SER_CMS_LIST_DVOL_SNAP_ERR                           = 8041
    MSG_SER_CMS_DVOL_SET_SNAPSHOT_PERIOD_ERR                 = 8043
    MSG_SER_CMS_DVOL_CREATE_BACKUP_IMAGE_ERR                 = 8044
    MSG_SER_CMS_UPDATE_CMS_ERR                               = 8048
    MSG_SER_CMS_DVOL_TEST_FAILOVER_DELETE_RS_ERR             = 8051
    MSG_SER_CMS_DISK_CLAIM_ERR                               = 8053
    MSG_SER_CMS_DVOL_STORAGE_REPAIR_ERR                      = 8067
    MSG_SER_CMS_CREATE_PLUN_ERR                              = 8079
    MSG_SER_CMS_DELETE_PLUN_ERR                              = 8080
    MSG_SER_CMS_RESIZE_PLUN_ERR                              = 8081
    MSG_SER_CMS_DVOL_LIST_PLUN_ERR                           = 8082
    MSG_SER_CMS_DVOL_ADD_TARGET_ERR                          = 8085
    MSG_SER_CMS_DVOL_DELETE_TARGET_ERR                       = 8086
    MSG_SER_CMS_DVOL_LIST_RECOVERY_PLAN_ERR                  = 8088
    MSG_SER_CMS_DVOL_CREATE_UPDATE_RECOVERY_PLAN_ERR         = 8089
    MSG_SER_CMS_DVOL_UPDATE_STUB_ERR                         = 8090
    MSG_SER_CMS_DVOL_LIST_TARGETS_ERR                        = 8091
    MSG_SER_CMS_DVOL_SET_WAN_THROTTLE_ERR                    = 8093
    MSG_SER_CMS_DISK_UNCLAIM_ERR                             = 8095
    MSG_SER_CMS_DVOL_RESIZE_ROW_POOL_ERR                     = 8096
    MSG_SER_CMS_DVOL_RESIZE_COW_POOL_ERR                     = 8097
    MSG_SER_CMS_DVOL_RESIZE_PRIMARY_ERR                      = 8098
    MSG_SER_CMS_DVOL_INSTALL_LRA_ERR                         = 8099
    MSG_SER_CMS_DVOL_INSTALL_MAKESTUB_ERR                    = 8100
    MSG_SER_CMS_DVOL_CONVERT_OOB_ERR                         = 8101
    MSG_SER_CMS_SRN_ADD_PEER_SRN_ERR                         = 8102
    MSG_SER_CMS_SRN_REMOVE_PEER_SRN_ERR                      = 8103
    MSG_SER_CMS_DVOL_ADD_VM_ERR                              = 8104
    MSG_SER_CMS_DVOL_SCHEDULE_SNAPSHOT_ERR                   = 8105
    MSG_SER_CMS_DVOL_SET_ERROR                               = 9005
    MSG_SER_SER_CREATE_DVOL_LEG                              = 12002
    MSG_SER_SER_DVOL_CONVERT_COW_TO_ROW                      = 12004
    MSG_SER_SER_DVOL_CONVERT_ROW_TO_COW                      = 12005
    MSG_SER_SER_START_DVOL_LEG                               = 12006
    MSG_SER_SER_STOP_DVOL_LEG                                = 12007
    MSG_SER_SER_TRANS_AUTH_DVOL                              = 12012
    MSG_SER_SER_CREATE_PLUN_RS                               = 12022
    MSG_SER_SER_DELETE_PLUN_RS                               = 12024
    MSG_SER_SER_RESIZE_PLUN_RS                               = 12026
    MSG_SER_SER_DVOL_SET_RESYNC_PERIOD_LEG                   = 12030
    MSG_SER_SER_DVOL_RESIZE_DISKS_RS                         = 12035
    MSG_SER_SER_DVOL_DELETE_LEG                              = 12036
    MSG_SER_SER_DVOL_ROLLBACK_RS                             = 12037
    MSG_SER_SER_DVOL_SNAPSHOT_RS                             = 12038
    MSG_SER_SER_DVOL_DELETE_OLD_DISKS_LEG                    = 12040
    MSG_SER_SER_DVOL_FAILBACK_RS                             = 12043
    MSG_SER_SER_DVOL_SBD_STOP_SYNC_RS                        = 12056
    MSG_SER_SER_DVOL_SET_SNAPSHOT_PERIOD_LEG                 = 12064
    MSG_SER_SER_CREATE_TARGET_RS                             = 12066
    MSG_SER_SER_DVOL_SNAPSHOT_SYNC                           = 12069
    MSG_SER_SER_DVOL_SNAPSHOT_SYNC_RS                        = 12070
    MSG_SER_SER_DVOL_DESTROY_RS                              = 12073
    MSG_SER_SER_DVOL_STORAGE_REPAIR_RS                       = 12079
    MSG_SER_SER_DVOL_LIST_PROP_RS                            = 12081
    MSG_SER_SER_RECONSTITUTE_DVOLS                           = 12082
    MSG_SER_SER_DVOL_RESERVE_SPACE_FOR_BACKUP_RS             = 12086
    MSG_SER_SER_DVOL_RELEASE_SPACE_FOR_BACKUP_RS             = 12087
    MSG_SER_SER_DVOL_ADD_TARGET_RS                           = 12088
    MSG_SER_SER_DVOL_DELETE_TARGET_RS                        = 12089
    MSG_SER_SER_DVOL_RESIZE_PRIMARY_RS                       = 12090
    MSG_SER_SER_DVOL_RESIZE_SNAPSHOT_DEV_RS                  = 12091
    MSG_SER_SER_DVOL_CREATE_RECOVERY_PLAN_RS                 = 12092
    MSG_SER_SER_DVOL_PROVISION_STUBS_RS                      = 12093
    MSG_SER_SER_DVOL_INVALID_ALL_SNAPSHOTS_RS                = 12097
    MSG_SER_SER_DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG       = 12098
    MSG_SER_SER_CREATE_DVOL_LEG_SUC                          = 13002
    MSG_SER_SER_DVOL_CONVERT_COW_TO_ROW_SUC                  = 13004
    MSG_SER_SER_DVOL_CONVERT_ROW_TO_COW_SUC                  = 13005
    MSG_SER_SER_START_DVOL_LEG_SUC                           = 13006
    MSG_SER_SER_STOP_DVOL_LEG_SUC                            = 13007
    MSG_SER_SER_TRANS_AUTH_DVOL_SUC                          = 13012
    MSG_SER_SER_CREATE_PLUN_RS_SUC                           = 13022
    MSG_SER_SER_DELETE_PLUN_RS_SUC                           = 13024
    MSG_SER_SER_RESIZE_PLUN_RS_SUC                           = 13026
    MSG_SER_SER_DVOL_SET_RESYNC_PERIOD_LEG_SUC               = 13030
    MSG_SER_SER_DVOL_RESIZE_DISKS_RS_SUC                     = 13035
    MSG_SER_SER_DVOL_DELETE_LEG_SUC                          = 13036
    MSG_SER_SER_DVOL_ROLLBACK_RS_SUC                         = 13037
    MSG_SER_SER_DVOL_SNAPSHOT_RS_SUC                         = 13038
    MSG_SER_SER_DVOL_DELETE_OLD_DISKS_LEG_SUC                = 13040
    MSG_SER_SER_DVOL_FAILBACK_RS_SUC                         = 13043
    MSG_SER_SER_DVOL_SBD_STOP_SYNC_RS_SUC                    = 13056
    MSG_SER_SER_DVOL_SET_SNAPSHOT_PERIOD_LEG_SUC             = 13064
    MSG_SER_SER_CREATE_TARGET_RS_SUC                         = 13066
    MSG_SER_SER_DVOL_SNAPSHOT_SYNC_SUC                       = 13069
    MSG_SER_SER_DVOL_SNAPSHOT_SYNC_RS_SUC                    = 13070
    MSG_SER_SER_DVOL_DESTROY_RS_SUC                          = 13073
    MSG_SER_SER_DVOL_STORAGE_REPAIR_RS_SUC                   = 13079
    MSG_SER_SER_DVOL_LIST_PROP_RS_SUC                        = 13081
    MSG_SER_SER_DVOL_RESERVE_SPACE_FOR_BACKUP_RS_SUC         = 13086
    MSG_SER_SER_DVOL_RELEASE_SPACE_FOR_BACKUP_RS_SUC         = 13087
    MSG_SER_SER_DVOL_ADD_TARGET_RS_SUC                       = 13088
    MSG_SER_SER_DVOL_DELETE_TARGET_RS_SUC                    = 13089
    MSG_SER_SER_DVOL_RESIZE_PRIMARY_RS_SUC                   = 13090
    MSG_SER_SER_DVOL_RESIZE_SNAPSHOT_DEV_RS_SUC              = 13091
    MSG_SER_SER_DVOL_CREATE_RECOVERY_PLAN_RS_SUC             = 13092
    MSG_SER_SER_DVOL_PROVISION_STUBS_RS_SUC                  = 13093
    MSG_SER_SER_DVOL_INVALID_ALL_SNAPSHOTS_RS_SUC            = 13097
    MSG_SER_SER_DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG_SUC   = 13098
    MSG_SER_SER_CREATE_DVOL_LEG_ERR                          = 14002
    MSG_SER_SER_DVOL_CONVERT_COW_TO_ROW_ERR                  = 14004
    MSG_SER_SER_DVOL_CONVERT_ROW_TO_COW_ERR                  = 14005
    MSG_SER_SER_START_DVOL_LEG_ERR                           = 14006
    MSG_SER_SER_STOP_DVOL_LEG_ERR                            = 14007
    MSG_SER_SER_TRANS_AUTH_DVOL_ERR                          = 14012
    MSG_SER_SER_CREATE_PLUN_RS_ERR                           = 14022
    MSG_SER_SER_DELETE_PLUN_RS_ERR                           = 14024
    MSG_SER_SER_RESIZE_PLUN_RS_ERR                           = 14026
    MSG_SER_SER_DVOL_SET_RESYNC_PERIOD_LEG_ERR               = 14030
    MSG_SER_SER_DVOL_RESIZE_DISKS_RS_ERR                     = 14035
    MSG_SER_SER_DVOL_DELETE_LEG_ERR                          = 14036
    MSG_SER_SER_DVOL_ROLLBACK_RS_ERR                         = 14037
    MSG_SER_SER_DVOL_SNAPSHOT_RS_ERR                         = 14038
    MSG_SER_SER_DVOL_DELETE_OLD_DISKS_LEG_ERR                = 14040
    MSG_SER_SER_DVOL_FAILBACK_RS_ERR                         = 14043
    MSG_SER_SER_DVOL_SBD_STOP_SYNC_RS_ERR                    = 14056
    MSG_SER_SER_DVOL_SET_SNAPSHOT_PERIOD_LEG_ERR             = 14064
    MSG_SER_SER_CREATE_TARGET_RS_ERR                         = 14066
    MSG_SER_SER_DVOL_SNAPSHOT_SYNC_ERR                       = 14069
    MSG_SER_SER_DVOL_SNAPSHOT_SYNC_RS_ERR                    = 14070
    MSG_SER_SER_DVOL_DESTROY_RS_ERR                          = 14073
    MSG_SER_SER_DVOL_STORAGE_REPAIR_RS_ERR                   = 14079
    MSG_SER_SER_DVOL_LIST_PROP_RS_ERR                        = 14081
    MSG_SER_SER_DVOL_RESERVE_SPACE_FOR_BACKUP_RS_ERR         = 14086
    MSG_SER_SER_DVOL_RELEASE_SPACE_FOR_BACKUP_RS_ERR         = 14087
    MSG_SER_SER_DVOL_ADD_TARGET_RS_ERR                       = 14088
    MSG_SER_SER_DVOL_DELETE_TARGET_RS_ERR                    = 14089
    MSG_SER_SER_DVOL_RESIZE_PRIMARY_RS_ERR                   = 14090
    MSG_SER_SER_DVOL_RESIZE_SNAPSHOT_DEV_RS_ERR              = 14091
    MSG_SER_SER_DVOL_CREATE_RECOVERY_PLAN_RS_ERR             = 14092
    MSG_SER_SER_DVOL_PROVISION_STUBS_RS_ERR                  = 14093
    MSG_SER_SER_DVOL_INVALID_ALL_SNAPSHOTS_RS_ERR            = 14097
    MSG_SER_SER_DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG_ERR   = 14098
    MSG_SER_THRD_CREATE_DVOL_CMS                             = 15001
    MSG_SER_THRD_CREATE_DVOL_LEG                             = 15002
    MSG_SER_THRD_START_DVOL_LEG                              = 15006
    MSG_SER_THRD_STOP_DVOL_LEG                               = 15007
    MSG_SER_THRD_DVOL_CONVERT_COW_TO_ROW                     = 15008
    MSG_SER_THRD_DVOL_CONVERT_COW_TO_ROW_RS                  = 15009
    MSG_SER_THRD_LIST_DVOL_PROP                              = 15010
    MSG_SER_THRD_DVOL_CONVERT_ROW_TO_COW                     = 15011
    MSG_SER_THRD_DVOL_CONVERT_ROW_TO_COW_RS                  = 15012
    MSG_SER_THRD_MIGRATE_DVOL                                = 15013
    MSG_SER_THRD_TRANS_AUTH_DVOL                             = 15014
    MSG_SER_THRD_SYNC_DVOL                                   = 15021
    MSG_SER_THRD_DVOL_START_TGT                              = 15028
    MSG_SER_THRD_CREATE_PLUN                                 = 15033
    MSG_SER_THRD_CREATE_PLUN_RS                              = 15034
    MSG_SER_THRD_SITE_REGISTER_LISTEN                        = 15036
    MSG_SER_THRD_SITE_REGISTER_SEND                          = 15037
    MSG_SER_THRD_SITE_UNREGISTER_LISTEN                      = 15038
    MSG_SER_THRD_SITE_UNREGISTER_SEND                        = 15039
    MSG_SER_THRD_DVOL_SBD_STOP_SYNC_RS                       = 15042
    MSG_SER_THRD_TIMER_REQUEST                               = 15049
    MSG_SER_THRD_SCHEDULE_EVENT                              = 15050
    MSG_SER_THRD_DVOL_SET_RESYNC_PERIOD                      = 15053
    MSG_SER_THRD_DVOL_SET_RESYNC_PERIOD_LEG                  = 15054
    MSG_SER_THRD_DVOL_DELETE_LEG                             = 15063
    MSG_SER_THRD_DVOL_RECONSTITUTE_MS                        = 15064
    MSG_SER_THRD_DVOL_ROLLBACK_RS                            = 15065
    MSG_SER_THRD_DVOL_RECONSTITUTE_RS                        = 15067
    MSG_SER_THRD_DVOL_UPDATE_STUB                            = 15068
    MSG_SER_THRD_DVOL_SNAPSHOT_RS                            = 15070
    MSG_SER_THRD_DVOL_DELETE                                 = 15071
    MSG_SER_THRD_DVOL_DELETE_OLD_DISKS_LEG                   = 15074
    MSG_SER_THRD_DVOL_SNAP_RS                                = 15075
    MSG_SER_THRD_DVOL_MANUAL_SNAPSHOT                        = 15076
    MSG_SER_THRD_DVOL_ROLLBACK                               = 15077
    MSG_SER_THRD_DVOL_CREATE_BACKUP_IMAGE                    = 15078
    MSG_SER_THRD_LIST_DVOL_SNAP                              = 15079
    MSG_SER_THRD_DVOL_FAILOVER                               = 15080
    MSG_SER_THRD_DVOL_FAILBACK_MS                            = 15081
    MSG_SER_THRD_DVOL_FAILBACK_RS                            = 15082
    MSG_SER_THRD_DVOL_FAILBACK_STOP_OLD_MASTER               = 15083
    MSG_SER_THRD_START_DVOL_MANAGER                          = 15084
    MSG_SER_THRD_DVOL_SBD_WAIT_FOR_SBD_ROLE                  = 15094
    MSG_SER_THRD_DVOL_PERIODIC_SNAPSHOT                      = 15097
    MSG_SER_THRD_DVOL_SCHEDULED_SNAPSHOT                     = 15098
    MSG_SER_THRD_DVOL_RESIZE_DISKS                           = 15102
    MSG_SER_THRD_DVOL_SET_SNAPSHOT_PERIOD                    = 15105
    MSG_SER_THRD_DVOL_SET_SNAPSHOT_PERIOD_LEG                = 15106
    MSG_SER_THRD_DVOL_SNAPSHOT_SYNC                          = 15110
    MSG_SER_THRD_DVOL_SNAPSHOT_SYNC_RS                       = 15111
    MSG_SER_THRD_TIMER_DESTROY_DVOL_TIMERS                   = 15113
    MSG_SER_THRD_DESTROY_SCHEDULED_EVENTS                    = 15114
    MSG_SER_THRD_DVOL_MANAGER_SHUTDOWN                       = 15119
    MSG_SER_THRD_DVOL_DESTROY_RS                             = 15120
    MSG_SER_THRD_DVOL_RESIZE_DISKS_RS                        = 15122
    MSG_SER_THRD_DVOL_STOP_ALL_TIMERS                        = 15123
    MSG_SER_THRD_DVOL_STOP_TARGET                            = 15125
    MSG_SER_THRD_DISK_CLAIM                                  = 15131
    MSG_SER_THRD_DVOL_STOP                                   = 15139
    MSG_SER_THRD_DVOL_STORAGE_REPAIR                         = 15145
    MSG_SER_THRD_DVOL_STORAGE_REPAIR_RS                      = 15146
    MSG_SER_THRD_DVOL_LIST_PROP_RS                           = 15148
    MSG_SER_THRD_DVOL_TEST_FAILOVER_DELETE_RS                = 15153
    MSG_SER_THRD_DVOL_RESERVE_SPACE_FOR_BACKUP_RS            = 15158
    MSG_SER_THRD_DVOL_RELEASE_SPACE_FOR_BACKUP_RS            = 15159
    MSG_SER_THRD_DELETE_PLUN                                 = 15166
    MSG_SER_THRD_DELETE_PLUN_RS                              = 15167
    MSG_SER_THRD_RESIZE_PLUN                                 = 15168
    MSG_SER_THRD_RESIZE_PLUN_RS                              = 15169
    MSG_SER_THRD_DVOL_LIST_PLUN                              = 15170
    MSG_SER_THRD_CREATE_TARGET_RS                            = 15172
    MSG_SER_THRD_DVOL_LIST_RECOVERY_PLAN                     = 15173
    MSG_SER_THRD_DVOL_CREATE_UPDATE_RECOVERY_PLAN            = 15174
    MSG_SER_THRD_MONITOR_TEST_FAILOVER_QUOTA                 = 15175
    MSG_SER_THRD_DVOL_ADD_TARGET                             = 15176
    MSG_SER_THRD_DVOL_ADD_TARGET_RS                          = 15177
    MSG_SER_THRD_DVOL_DELETE_TARGET                          = 15178
    MSG_SER_THRD_DVOL_DELETE_TARGET_RS                       = 15179
    MSG_SER_THRD_DVOL_LIST_TARGETS                           = 15180
    MSG_SER_THRD_DVOL_SET_WAN_THROTTLE                       = 15181
    MSG_SER_THRD_DISK_UNCLAIM                                = 15183
    MSG_SER_THRD_DVOL_RESIZE_ROW_POOL                        = 15184
    MSG_SER_THRD_DVOL_RESIZE_COW_POOL                        = 15185
    MSG_SER_THRD_DVOL_RESIZE_PRIMARY                         = 15186
    MSG_SER_THRD_DVOL_RESIZE_PRIMARY_RS                      = 15187
    MSG_SER_THRD_DVOL_INSTALL_LRA                            = 15188
    MSG_SER_THRD_DVOL_INSTALL_MAKESTUB                       = 15189
    MSG_SER_THRD_DVOL_CONVERT_OOB                            = 15190
    MSG_SER_THRD_DVOL_RESIZE_SNAPSHOT_DEV_RS                 = 15192
    MSG_SER_THRD_DVOL_CREATE_RECOVERY_PLAN_RS                = 15193
    MSG_SER_THRD_DVOL_PROVISION_STUBS_RS                     = 15194
    MSG_SER_THRD_SRN_ADD_PEER_SRN                            = 15196
    MSG_SER_THRD_SRN_REMOVE_PEER_SRN                         = 15197
    MSG_SER_THRD_DVOL_ADD_VM                                 = 15199
    MSG_SER_THRD_DVOL_INVALID_ALL_SNAPSHOTS_RS               = 15201
    MSG_SER_THRD_DVOL_SCHEDULE_SNAPSHOT                      = 15202
    MSG_SER_THRD_DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG      = 15203
    MSG_THRD_SER_CREATE_DVOL_CMS_SUC                         = 16001
    MSG_THRD_SER_CREATE_DVOL_LEG_SUC                         = 16002
    MSG_THRD_SER_START_DVOL_LEG_SUC                          = 16006
    MSG_THRD_SER_STOP_DVOL_LEG_SUC                           = 16007
    MSG_THRD_SER_DVOL_CONVERT_COW_TO_ROW_SUC                 = 16008
    MSG_THRD_SER_DVOL_CONVERT_COW_TO_ROW_RS_SUC              = 16009
    MSG_THRD_SER_LIST_DVOL_PROP_SUC                          = 16010
    MSG_THRD_SER_DVOL_CONVERT_ROW_TO_COW_SUC                 = 16011
    MSG_THRD_SER_DVOL_CONVERT_ROW_TO_COW_RS_SUC              = 16012
    MSG_THRD_SER_MIGRATE_DVOL_SUC                            = 16013
    MSG_THRD_SER_TRANS_AUTH_DVOL_SUC                         = 16014
    MSG_THRD_SER_DVOL_START_TGT_SUC                          = 16028
    MSG_THRD_SER_CREATE_PLUN_SUC                             = 16033
    MSG_THRD_SER_CREATE_PLUN_RS_SUC                          = 16034
    MSG_THRD_SER_SITE_REGISTER_LISTEN_SUC                    = 16036
    MSG_THRD_SER_SITE_REGISTER_SEND_SUC                      = 16037
    MSG_THRD_SER_SITE_UNREGISTER_LISTEN_SUC                  = 16038
    MSG_THRD_SER_SITE_UNREGISTER_SEND_SUC                    = 16039
    MSG_THRD_SER_DVOL_SBD_STOP_SYNC_RS_SUC                   = 16042
    MSG_THRD_SER_DVOL_SET_RESYNC_PERIOD_SUC                  = 16053
    MSG_THRD_SER_DVOL_SET_RESYNC_PERIOD_LEG_SUC              = 16054
    MSG_THRD_SER_DVOL_DELETE_LEG_SUC                         = 16063
    MSG_THRD_SER_DVOL_RECONSTITUTE_MS_SUC                    = 16064
    MSG_THRD_SER_DVOL_ROLLBACK_RS_SUC                        = 16065
    MSG_THRD_SER_DVOL_RECONSTITUTE_RS_SUC                    = 16067
    MSG_THRD_SER_DVOL_UPDATE_STUB_SUC                        = 16068
    MSG_THRD_SER_DVOL_SNAPSHOT_RS_SUC                        = 16070
    MSG_THRD_SER_DVOL_DELETE_SUC                             = 16071
    MSG_THRD_SER_DVOL_DELETE_OLD_DISKS_LEG_SUC               = 16074
    MSG_THRD_SER_DVOL_SNAP_RS_SUC                            = 16075
    MSG_THRD_SER_DVOL_MANUAL_SNAPSHOT_SUC                    = 16076
    MSG_THRD_SER_DVOL_ROLLBACK_SUC                           = 16077
    MSG_THRD_SER_DVOL_CREATE_BACKUP_IMAGE_SUC                = 16078
    MSG_THRD_SER_LIST_DVOL_SNAP_SUC                          = 16079
    MSG_THRD_SER_DVOL_FAILOVER_SUC                           = 16080
    MSG_THRD_SER_DVOL_FAILBACK_MS_SUC                        = 16081
    MSG_THRD_SER_DVOL_FAILBACK_RS_SUC                        = 16082
    MSG_THRD_SER_DVOL_FAILBACK_STOP_OLD_MASTER_SUC           = 16083
    MSG_THRD_SER_START_DVOL_MANAGER_SUC                      = 16084
    MSG_THRD_SER_DVOL_SBD_WAIT_FOR_SBD_ROLE_SUC              = 16094
    MSG_THRD_SER_DVOL_RESIZE_DISKS_SUC                       = 16102
    MSG_THRD_SER_DVOL_SET_SNAPSHOT_PERIOD_SUC                = 16105
    MSG_THRD_SER_DVOL_SET_SNAPSHOT_PERIOD_LEG_SUC            = 16106
    MSG_THRD_SER_DVOL_SNAPSHOT_SYNC_SUC                      = 16110
    MSG_THRD_SER_DVOL_SNAPSHOT_SYNC_RS_SUC                   = 16111
    MSG_THRD_SER_DVOL_MANAGER_SHUTDOWN_SUC                   = 16119
    MSG_THRD_SER_DVOL_DESTROY_RS_SUC                         = 16120
    MSG_THRD_SER_DVOL_RESIZE_DISKS_RS_SUC                    = 16122
    MSG_THRD_SER_DVOL_STOP_ALL_TIMERS_SUC                    = 16123
    MSG_THRD_SER_DVOL_STOP_TARGET_SUC                        = 16125
    MSG_THRD_SER_DISK_CLAIM_SUC                              = 16131
    MSG_THRD_SER_DVOL_STOP_SUC                               = 16139
    MSG_THRD_SER_DVOL_STORAGE_REPAIR_SUC                     = 16145
    MSG_THRD_SER_DVOL_STORAGE_REPAIR_RS_SUC                  = 16146
    MSG_THRD_SER_DVOL_LIST_PROP_RS_SUC                       = 16148
    MSG_THRD_SER_DVOL_TEST_FAILOVER_DELETE_RS_SUC            = 16153
    MSG_THRD_SER_DVOL_RESERVE_SPACE_FOR_BACKUP_RS_SUC        = 16158
    MSG_THRD_SER_DVOL_RELEASE_SPACE_FOR_BACKUP_RS_SUC        = 16159
    MSG_THRD_SER_DELETE_PLUN_SUC                             = 16166
    MSG_THRD_SER_DELETE_PLUN_RS_SUC                          = 16167
    MSG_THRD_SER_RESIZE_PLUN_SUC                             = 16168
    MSG_THRD_SER_RESIZE_PLUN_RS_SUC                          = 16169
    MSG_THRD_SER_DVOL_LIST_PLUN_SUC                          = 16170
    MSG_THRD_SER_CREATE_TARGET_RS_SUC                        = 16172
    MSG_THRD_SER_DVOL_LIST_RECOVERY_PLAN_SUC                 = 16173
    MSG_THRD_SER_DVOL_CREATE_UPDATE_RECOVERY_PLAN_SUC        = 16174
    MSG_THRD_SER_MONITOR_TEST_FAILOVER_QUOTA_SUC             = 16175
    MSG_THRD_SER_DVOL_ADD_TARGET_SUC                         = 16176
    MSG_THRD_SER_DVOL_ADD_TARGET_RS_SUC                      = 16177
    MSG_THRD_SER_DVOL_DELETE_TARGET_SUC                      = 16178
    MSG_THRD_SER_DVOL_DELETE_TARGET_RS_SUC                   = 16179
    MSG_THRD_SER_DVOL_LIST_TARGETS_SUC                       = 16180
    MSG_THRD_SER_DVOL_SET_WAN_THROTTLE_SUC                   = 16181
    MSG_THRD_SER_DISK_UNCLAIM_SUC                            = 16183
    MSG_THRD_SER_DVOL_RESIZE_ROW_POOL_SUC                    = 16184
    MSG_THRD_SER_DVOL_RESIZE_COW_POOL_SUC                    = 16185
    MSG_THRD_SER_DVOL_RESIZE_PRIMARY_SUC                     = 16186
    MSG_THRD_SER_DVOL_RESIZE_PRIMARY_RS_SUC                  = 16187
    MSG_THRD_SER_DVOL_INSTALL_LRA_SUC                        = 16188
    MSG_THRD_SER_DVOL_INSTALL_MAKESTUB_SUC                   = 16189
    MSG_THRD_SER_DVOL_CONVERT_OOB_SUC                        = 16190
    MSG_THRD_SER_DVOL_RESIZE_SNAPSHOT_DEV_RS_SUC             = 16192
    MSG_THRD_SER_DVOL_CREATE_RECOVERY_PLAN_RS_SUC            = 16193
    MSG_THRD_SER_DVOL_PROVISION_STUBS_RS_SUC                 = 16194
    MSG_THRD_SER_SRN_ADD_PEER_SRN_SUC                        = 16196
    MSG_THRD_SER_SRN_REMOVE_PEER_SRN_SUC                     = 16197
    MSG_THRD_SER_DVOL_ADD_VM_SUC                             = 16199
    MSG_THRD_SER_DVOL_INVALID_ALL_SNAPSHOTS_RS_SUC           = 16201
    MSG_THRD_SER_DVOL_SCHEDULE_SNAPSHOT_SUC                  = 16202
    MSG_THRD_SER_DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG_SUC  = 16203
    MSG_THRD_SER_CREATE_DVOL_CMS_ERR                         = 17001
    MSG_THRD_SER_CREATE_DVOL_LEG_ERR                         = 17002
    MSG_THRD_SER_START_DVOL_LEG_ERR                          = 17006
    MSG_THRD_SER_STOP_DVOL_LEG_ERR                           = 17007
    MSG_THRD_SER_DVOL_CONVERT_COW_TO_ROW_ERR                 = 17008
    MSG_THRD_SER_DVOL_CONVERT_COW_TO_ROW_RS_ERR              = 17009
    MSG_THRD_SER_LIST_DVOL_PROP_ERR                          = 17010
    MSG_THRD_SER_DVOL_CONVERT_ROW_TO_COW_ERR                 = 17011
    MSG_THRD_SER_DVOL_CONVERT_ROW_TO_COW_RS_ERR              = 17012
    MSG_THRD_SER_MIGRATE_DVOL_ERR                            = 17013
    MSG_THRD_SER_TRANS_AUTH_DVOL_ERR                         = 17014
    MSG_THRD_SER_SYNC_DVOL_ERR                               = 17021
    MSG_THRD_SER_DVOL_START_TGT_ERR                          = 17028
    MSG_THRD_SER_CREATE_PLUN_ERR                             = 17033
    MSG_THRD_SER_CREATE_PLUN_RS_ERR                          = 17034
    MSG_THRD_SER_SITE_REGISTER_LISTEN_ERR                    = 17036
    MSG_THRD_SER_SITE_REGISTER_SEND_ERR                      = 17037
    MSG_THRD_SER_SITE_UNREGISTER_LISTEN_ERR                  = 17038
    MSG_THRD_SER_SITE_UNREGISTER_SEND_ERR                    = 17039
    MSG_THRD_SER_DVOL_SBD_STOP_SYNC_RS_ERR                   = 17042
    MSG_THRD_SER_DVOL_SET_RESYNC_PERIOD_ERR                  = 17053
    MSG_THRD_SER_DVOL_SET_RESYNC_PERIOD_LEG_ERR              = 17054
    MSG_THRD_SER_DVOL_DELETE_LEG_ERR                         = 17063
    MSG_THRD_SER_DVOL_RECONSTITUTE_MS_ERR                    = 17064
    MSG_THRD_SER_DVOL_ROLLBACK_RS_ERR                        = 17065
    MSG_THRD_SER_DVOL_RECONSTITUTE_RS_ERR                    = 17067
    MSG_THRD_SER_DVOL_UPDATE_STUB_ERR                        = 17068
    MSG_THRD_SER_DVOL_SNAPSHOT_RS_ERR                        = 17070
    MSG_THRD_SER_DVOL_DELETE_ERR                             = 17071
    MSG_THRD_SER_DVOL_DELETE_OLD_DISKS_LEG_ERR               = 17074
    MSG_THRD_SER_DVOL_SNAP_RS_ERR                            = 17075
    MSG_THRD_SER_DVOL_MANUAL_SNAPSHOT_ERR                    = 17076
    MSG_THRD_SER_DVOL_ROLLBACK_ERR                           = 17077
    MSG_THRD_SER_DVOL_CREATE_BACKUP_IMAGE_ERR                = 17078
    MSG_THRD_SER_LIST_DVOL_SNAP_ERR                          = 17079
    MSG_THRD_SER_DVOL_FAILOVER_ERR                           = 17080
    MSG_THRD_SER_DVOL_FAILBACK_MS_ERR                        = 17081
    MSG_THRD_SER_DVOL_FAILBACK_RS_ERR                        = 17082
    MSG_THRD_SER_DVOL_FAILBACK_STOP_OLD_MASTER_ERR           = 17083
    MSG_THRD_SER_START_DVOL_MANAGER_ERR                      = 17084
    MSG_THRD_SER_DVOL_SBD_WAIT_FOR_SBD_ROLE_ERR              = 17094
    MSG_THRD_SER_DVOL_RESIZE_DISKS_ERR                       = 17102
    MSG_THRD_SER_DVOL_SET_SNAPSHOT_PERIOD_ERR                = 17105
    MSG_THRD_SER_DVOL_SET_SNAPSHOT_PERIOD_LEG_ERR            = 17106
    MSG_THRD_SER_DVOL_SNAPSHOT_SYNC_ERR                      = 17110
    MSG_THRD_SER_DVOL_SNAPSHOT_SYNC_RS_ERR                   = 17111
    MSG_THRD_SER_DVOL_MANAGER_SHUTDOWN_ERR                   = 17119
    MSG_THRD_SER_DVOL_DESTROY_RS_ERR                         = 17120
    MSG_THRD_SER_DVOL_RESIZE_DISKS_RS_ERR                    = 17122
    MSG_THRD_SER_DVOL_STOP_ALL_TIMERS_ERR                    = 17123
    MSG_THRD_SER_DVOL_STOP_TARGET_ERR                        = 17125
    MSG_THRD_SER_DISK_CLAIM_ERR                              = 17131
    MSG_THRD_SER_DVOL_STOP_ERR                               = 17139
    MSG_THRD_SER_DVOL_STORAGE_REPAIR_ERR                     = 17145
    MSG_THRD_SER_DVOL_STORAGE_REPAIR_RS_ERR                  = 17146
    MSG_THRD_SER_DVOL_LIST_PROP_RS_ERR                       = 17148
    MSG_THRD_SER_DVOL_TEST_FAILOVER_DELETE_RS_ERR            = 17153
    MSG_THRD_SER_DVOL_RESERVE_SPACE_FOR_BACKUP_RS_ERR        = 17158
    MSG_THRD_SER_DVOL_RELEASE_SPACE_FOR_BACKUP_RS_ERR        = 17159
    MSG_THRD_SER_DELETE_PLUN_ERR                             = 17166
    MSG_THRD_SER_DELETE_PLUN_RS_ERR                          = 17167
    MSG_THRD_SER_RESIZE_PLUN_ERR                             = 17168
    MSG_THRD_SER_RESIZE_PLUN_RS_ERR                          = 17169
    MSG_THRD_SER_DVOL_LIST_PLUN_ERR                          = 17170
    MSG_THRD_SER_CREATE_TARGET_RS_ERR                        = 17172
    MSG_THRD_SER_DVOL_LIST_RECOVERY_PLAN_ERR                 = 17173
    MSG_THRD_SER_DVOL_CREATE_UPDATE_RECOVERY_PLAN_ERR        = 17174
    MSG_THRD_SER_MONITOR_TEST_FAILOVER_QUOTA_ERR             = 17175
    MSG_THRD_SER_DVOL_ADD_TARGET_ERR                         = 17176
    MSG_THRD_SER_DVOL_ADD_TARGET_RS_ERR                      = 17177
    MSG_THRD_SER_DVOL_DELETE_TARGET_ERR                      = 17178
    MSG_THRD_SER_DVOL_DELETE_TARGET_RS_ERR                   = 17179
    MSG_THRD_SER_DVOL_LIST_TARGETS_ERR                       = 17180
    MSG_THRD_SER_DVOL_SET_WAN_THROTTLE_ERR                   = 17181
    MSG_THRD_SER_DISK_UNCLAIM_ERR                            = 17183
    MSG_THRD_SER_DVOL_RESIZE_ROW_POOL_ERR                    = 17184
    MSG_THRD_SER_DVOL_RESIZE_COW_POOL_ERR                    = 17185
    MSG_THRD_SER_DVOL_RESIZE_PRIMARY_ERR                     = 17186
    MSG_THRD_SER_DVOL_RESIZE_PRIMARY_RS_ERR                  = 17187
    MSG_THRD_SER_DVOL_INSTALL_LRA_ERR                        = 17188
    MSG_THRD_SER_DVOL_INSTALL_MAKESTUB_ERR                   = 17189
    MSG_THRD_SER_DVOL_CONVERT_OOB_ERR                        = 17190
    MSG_THRD_SER_DVOL_RESIZE_SNAPSHOT_DEV_RS_ERR             = 17192
    MSG_THRD_SER_DVOL_CREATE_RECOVERY_PLAN_RS_ERR            = 17193
    MSG_THRD_SER_DVOL_PROVISION_STUBS_RS_ERR                 = 17194
    MSG_THRD_SER_SRN_ADD_PEER_SRN_ERR                        = 17196
    MSG_THRD_SER_SRN_REMOVE_PEER_SRN_ERR                     = 17197
    MSG_THRD_SER_DVOL_ADD_VM_ERR                             = 17199
    MSG_THRD_SER_DVOL_INVALID_ALL_SNAPSHOTS_RS_ERR           = 17201
    MSG_THRD_SER_DVOL_SCHEDULE_SNAPSHOT_ERR                  = 17202
    MSG_THRD_SER_DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG_ERR  = 17203
    MSG_THRD_SER_CREATE_DVOL_LEG                             = 18002
    MSG_THRD_SER_STOP                                        = 18004
    MSG_THRD_SER_START_DVOL_LEG                              = 18006
    MSG_THRD_SER_STOP_DVOL_LEG                               = 18007
    MSG_THRD_SER_DVOL_CONVERT_COW_TO_ROW                     = 18008
    MSG_THRD_SER_DVOL_CONVERT_COW_TO_ROW_RS                  = 18009
    MSG_THRD_SER_DVOL_CONVERT_ROW_TO_COW                     = 18011
    MSG_THRD_SER_DVOL_CONVERT_ROW_TO_COW_RS                  = 18012
    MSG_THRD_SER_MIGRATE_DVOL                                = 18013
    MSG_THRD_SER_TRANS_AUTH_DVOL                             = 18014
    MSG_THRD_SER_SYNC_DVOL                                   = 18018
    MSG_THRD_SER_DVOL_START_TGT                              = 18025
    MSG_THRD_SER_DVOL_MANAGER_SHUTDOWN                       = 18028
    MSG_THRD_SER_CREATE_PLUN_RS                              = 18030
    MSG_THRD_SER_SITE_REGISTER_LISTEN                        = 18031
    MSG_THRD_SER_SITE_REGISTER_SEND                          = 18032
    MSG_THRD_SER_SITE_UNREGISTER_LISTEN                      = 18033
    MSG_THRD_SER_SITE_UNREGISTER_SEND                        = 18034
    MSG_THRD_SER_DVOL_SBD_STOP_SYNC_RS                       = 18037
    MSG_THRD_SER_DVOL_SBD_WAIT_FOR_SBD_ROLE                  = 18040
    MSG_THRD_SER_TIMER_REQUEST                               = 18043
    MSG_THRD_SER_SCHEDULE_EVENT                              = 18044
    MSG_THRD_SER_DVOL_SET_RESYNC_PERIOD_LEG                  = 18046
    MSG_THRD_SER_DVOL_DELETE_LEG                             = 18053
    MSG_THRD_SER_DVOL_ROLLBACK_RS                            = 18054
    MSG_THRD_SER_DVOL_SNAPSHOT_RS                            = 18055
    MSG_THRD_SER_DVOL_DELETE_OLD_DISKS_LEG                   = 18057
    MSG_THRD_SER_DVOL_SNAP_RS                                = 18058
    MSG_THRD_SER_DVOL_PERIODIC_SNAPSHOT                      = 18059
    MSG_THRD_SER_DVOL_ROLLBACK                               = 18060
    MSG_THRD_SER_DVOL_FAILBACK_RS                            = 18061
    MSG_THRD_SER_DVOL_FAILBACK_STOP_OLD_MASTER               = 18062
    MSG_THRD_SER_DVOL_FAILBACK_MS                            = 18063
    MSG_THRD_SER_DVOL_DELETE_SNAPSHOTS                       = 18066
    MSG_THRD_SER_DVOL_STOP_TARGET                            = 18068
    MSG_THRD_SER_DVOL_RESIZE_DISKS                           = 18075
    MSG_THRD_SER_DVOL_RESIZE_DISKS_RS                        = 18076
    MSG_THRD_SER_DVOL_STOP_ALL_TIMERS                        = 18083
    MSG_THRD_SER_DVOL_SET_SNAPSHOT_PERIOD_LEG                = 18085
    MSG_THRD_SER_DVOL_SNAPSHOT_SYNC_RS                       = 18092
    MSG_THRD_SER_TIMER_DESTROY_DVOL_TIMERS                   = 18095
    MSG_THRD_SER_DESTROY_SCHEDULED_EVENTS                    = 18096
    MSG_THRD_SER_DGCOM_REPORT_NODE_STATUS                    = 18099
    MSG_THRD_SER_DVOL_DESTROY_RS                             = 18101
    MSG_THRD_SER_DVOL_SNAPSHOT                               = 18102
    MSG_THRD_SER_DVOL_SET_ERROR                              = 18103
    MSG_THRD_SER_DVOL_STOP                                   = 18114
    MSG_THRD_SER_DVOL_STORAGE_REPAIR                         = 18116
    MSG_THRD_SER_DVOL_STORAGE_REPAIR_RS                      = 18117
    MSG_THRD_SER_DVOL_LIST_PROP_RS                           = 18119
    MSG_THRD_SER_DVOL_RESERVE_SPACE_FOR_BACKUP_RS            = 18123
    MSG_THRD_SER_DVOL_RELEASE_SPACE_FOR_BACKUP_RS            = 18124
    MSG_THRD_SER_DELETE_PLUN_RS                              = 18129
    MSG_THRD_SER_RESIZE_PLUN_RS                              = 18130
    MSG_THRD_SER_CREATE_TARGET_RS                            = 18133
    MSG_THRD_SER_MONITOR_TEST_FAILOVER_QUOTA                 = 18134
    MSG_THRD_SER_DVOL_ADD_TARGET_RS                          = 18135
    MSG_THRD_SER_DVOL_RESIZE_PRIMARY_RS                      = 18136
    MSG_THRD_SER_DVOL_RESIZE_SNAPSHOT_DEV_RS                 = 18137
    MSG_THRD_SER_DVOL_CREATE_RECOVERY_PLAN_RS                = 18138
    MSG_THRD_SER_DVOL_PROVISION_STUBS_RS                     = 18139
    MSG_THRD_SER_DVOL_INVALID_ALL_SNAPSHOTS_RS               = 18143
    MSG_THRD_SER_DVOL_SCHEDULED_SNAPSHOT                     = 18144
    MSG_THRD_SER_DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG      = 18145
    MSG_THRD_SER_RECONSTITUTION_TIMER                        = 18146
    MSG_THRD_SER_DVOL_DELETE_TARGET_RS                       = 18179
    MSG_SER_THRD_CREATE_DVOL_LEG_SUC                         = 19002
    MSG_SER_THRD_START_DVOL_LEG_SUC                          = 19006
    MSG_SER_THRD_STOP_DVOL_LEG_SUC                           = 19007
    MSG_SER_THRD_DVOL_CONVERT_COW_TO_ROW_SUC                 = 19008
    MSG_SER_THRD_DVOL_CONVERT_COW_TO_ROW_RS_SUC              = 19009
    MSG_SER_THRD_DVOL_CONVERT_ROW_TO_COW_SUC                 = 19011
    MSG_SER_THRD_DVOL_CONVERT_ROW_TO_COW_RS_SUC              = 19012
    MSG_SER_THRD_MIGRATE_DVOL_SUC                            = 19013
    MSG_SER_THRD_TRANS_AUTH_DVOL_SUC                         = 19014
    MSG_SER_THRD_DVOL_START_TGT_SUC                          = 19025
    MSG_SER_THRD_CREATE_PLUN_RS_SUC                          = 19030
    MSG_SER_THRD_SITE_REGISTER_LISTEN_SUC                    = 19031
    MSG_SER_THRD_SITE_REGISTER_SEND_SUC                      = 19032
    MSG_SER_THRD_SITE_UNREGISTER_LISTEN_SUC                  = 19033
    MSG_SER_THRD_SITE_UNREGISTER_SEND_SUC                    = 19034
    MSG_SER_THRD_DVOL_SBD_STOP_SYNC_RS_SUC                   = 19037
    MSG_SER_THRD_DVOL_SBD_WAIT_FOR_SBD_ROLE_SUC              = 19040
    MSG_SER_THRD_DVOL_SET_RESYNC_PERIOD_LEG_SUC              = 19046
    MSG_SER_THRD_DVOL_DELETE_LEG_SUC                         = 19053
    MSG_SER_THRD_DVOL_ROLLBACK_RS_SUC                        = 19054
    MSG_SER_THRD_DVOL_SNAPSHOT_RS_SUC                        = 19055
    MSG_SER_THRD_DVOL_DELETE_OLD_DISKS_LEG_SUC               = 19057
    MSG_SER_THRD_DVOL_SNAP_RS_SUC                            = 19058
    MSG_SER_THRD_DVOL_ROLLBACK_SUC                           = 19060
    MSG_SER_THRD_DVOL_FAILBACK_RS_SUC                        = 19061
    MSG_SER_THRD_DVOL_FAILBACK_STOP_OLD_MASTER_SUC           = 19062
    MSG_SER_THRD_DVOL_FAILBACK_MS_SUC                        = 19063
    MSG_SER_THRD_DVOL_DELETE_SNAPSHOTS_SUC                   = 19066
    MSG_SER_THRD_DVOL_STOP_TARGET_SUC                        = 19068
    MSG_SER_THRD_DVOL_RESIZE_DISKS_SUC                       = 19075
    MSG_SER_THRD_DVOL_RESIZE_DISKS_RS_SUC                    = 19076
    MSG_SER_THRD_DVOL_STOP_ALL_TIMERS_SUC                    = 19083
    MSG_SER_THRD_DVOL_SET_SNAPSHOT_PERIOD_LEG_SUC            = 19085
    MSG_SER_THRD_DVOL_SNAPSHOT_SYNC_RS_SUC                   = 19092
    MSG_SER_THRD_DGCOM_REPORT_NODE_STATUS_SUC                = 19099
    MSG_SER_THRD_DVOL_DESTROY_RS_SUC                         = 19101
    MSG_SER_THRD_DVOL_SNAPSHOT_SUC                           = 19102
    MSG_SER_THRD_DVOL_TEST_FAILOVER_DELETE_RS_SUC            = 19112
    MSG_SER_THRD_DVOL_STOP_SUC                               = 19114
    MSG_SER_THRD_DVOL_STORAGE_REPAIR_SUC                     = 19116
    MSG_SER_THRD_DVOL_STORAGE_REPAIR_RS_SUC                  = 19117
    MSG_SER_THRD_DVOL_LIST_PROP_RS_SUC                       = 19119
    MSG_SER_THRD_DVOL_RESERVE_SPACE_FOR_BACKUP_RS_SUC        = 19123
    MSG_SER_THRD_DVOL_RELEASE_SPACE_FOR_BACKUP_RS_SUC        = 19124
    MSG_SER_THRD_DELETE_PLUN_RS_SUC                          = 19129
    MSG_SER_THRD_RESIZE_PLUN_RS_SUC                          = 19130
    MSG_SER_THRD_CREATE_TARGET_RS_SUC                        = 19133
    MSG_SER_THRD_DVOL_ADD_TARGET_RS_SUC                      = 19135
    MSG_SER_THRD_DVOL_RESIZE_PRIMARY_RS_SUC                  = 19136
    MSG_SER_THRD_DVOL_RESIZE_SNAPSHOT_DEV_RS_SUC             = 19137
    MSG_SER_THRD_DVOL_CREATE_RECOVERY_PLAN_RS_SUC            = 19138
    MSG_SER_THRD_DVOL_PROVISION_STUBS_RS_SUC                 = 19139
    MSG_SER_THRD_DVOL_INVALID_ALL_SNAPSHOTS_RS_SUC           = 19143
    MSG_SER_THRD_DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG_SUC  = 19145
    MSG_SER_THRD_DVOL_DELETE_TARGET_RS_SUC                   = 19179
    MSG_SER_THRD_CREATE_DVOL_LEG_ERR                         = 20002
    MSG_SER_THRD_START_DVOL_LEG_ERR                          = 20006
    MSG_SER_THRD_STOP_DVOL_LEG_ERR                           = 20007
    MSG_SER_THRD_DVOL_CONVERT_COW_TO_ROW_ERR                 = 20008
    MSG_SER_THRD_DVOL_CONVERT_COW_TO_ROW_RS_ERR              = 20009
    MSG_SER_THRD_DVOL_CONVERT_ROW_TO_COW_ERR                 = 20011
    MSG_SER_THRD_DVOL_CONVERT_ROW_TO_COW_RS_ERR              = 20012
    MSG_SER_THRD_MIGRATE_DVOL_ERR                            = 20013
    MSG_SER_THRD_TRANS_AUTH_DVOL_ERR                         = 20014
    MSG_SER_THRD_DVOL_START_TGT_ERR                          = 20025
    MSG_SER_THRD_CREATE_PLUN_RS_ERR                          = 20030
    MSG_SER_THRD_SITE_REGISTER_LISTEN_ERR                    = 20031
    MSG_SER_THRD_SITE_REGISTER_SEND_ERR                      = 20032
    MSG_SER_THRD_SITE_UNREGISTER_LISTEN_ERR                  = 20033
    MSG_SER_THRD_SITE_UNREGISTER_SEND_ERR                    = 20034
    MSG_SER_THRD_DVOL_SBD_STOP_SYNC_RS_ERR                   = 20037
    MSG_SER_THRD_DVOL_SBD_WAIT_FOR_SBD_ROLE_ERR              = 20040
    MSG_SER_THRD_DVOL_SET_RESYNC_PERIOD_LEG_ERR              = 20046
    MSG_SER_THRD_DVOL_DELETE_LEG_ERR                         = 20053
    MSG_SER_THRD_DVOL_ROLLBACK_RS_ERR                        = 20054
    MSG_SER_THRD_DVOL_SNAPSHOT_RS_ERR                        = 20055
    MSG_SER_THRD_DVOL_DELETE_OLD_DISKS_LEG_ERR               = 20057
    MSG_SER_THRD_DVOL_SNAP_RS_ERR                            = 20058
    MSG_SER_THRD_DVOL_ROLLBACK_ERR                           = 20060
    MSG_SER_THRD_DVOL_FAILBACK_RS_ERR                        = 20061
    MSG_SER_THRD_DVOL_FAILBACK_STOP_OLD_MASTER_ERR           = 20062
    MSG_SER_THRD_DVOL_FAILBACK_MS_ERR                        = 20063
    MSG_SER_THRD_DVOL_DELETE_SNAPSHOTS_ERR                   = 20066
    MSG_SER_THRD_DVOL_STOP_TARGET_ERR                        = 20068
    MSG_SER_THRD_DVOL_RESIZE_DISKS_ERR                       = 20075
    MSG_SER_THRD_DVOL_RESIZE_DISKS_RS_ERR                    = 20076
    MSG_SER_THRD_DVOL_STOP_ALL_TIMERS_ERR                    = 20083
    MSG_SER_THRD_DVOL_SET_SNAPSHOT_PERIOD_LEG_ERR            = 20085
    MSG_SER_THRD_DVOL_SNAPSHOT_SYNC_RS_ERR                   = 20092
    MSG_SER_THRD_DGCOM_REPORT_NODE_STATUS_ERR                = 20099
    MSG_SER_THRD_DVOL_DESTROY_RS_ERR                         = 20101
    MSG_SER_THRD_DVOL_SNAPSHOT_ERR                           = 20102
    MSG_SER_THRD_DVOL_TEST_FAILOVER_DELETE_RS_ERR            = 20112
    MSG_SER_THRD_DVOL_STOP_ERR                               = 20114
    MSG_SER_THRD_DVOL_STORAGE_REPAIR_ERR                     = 20116
    MSG_SER_THRD_DVOL_STORAGE_REPAIR_RS_ERR                  = 20117
    MSG_SER_THRD_DVOL_LIST_PROP_RS_ERR                       = 20119
    MSG_SER_THRD_DVOL_RESERVE_SPACE_FOR_BACKUP_RS_ERR        = 20123
    MSG_SER_THRD_DVOL_RELEASE_SPACE_FOR_BACKUP_RS_ERR        = 20124
    MSG_SER_THRD_DELETE_PLUN_RS_ERR                          = 20129
    MSG_SER_THRD_RESIZE_PLUN_RS_ERR                          = 20130
    MSG_SER_THRD_CREATE_TARGET_RS_ERR                        = 20133
    MSG_SER_THRD_DVOL_ADD_TARGET_RS_ERR                      = 20135
    MSG_SER_THRD_DVOL_RESIZE_PRIMARY_RS_ERR                  = 20136
    MSG_SER_THRD_DVOL_RESIZE_SNAPSHOT_DEV_RS_ERR             = 20137
    MSG_SER_THRD_DVOL_CREATE_RECOVERY_PLAN_RS_ERR            = 20138
    MSG_SER_THRD_DVOL_PROVISION_STUBS_RS_ERR                 = 20139
    MSG_SER_THRD_DVOL_INVALID_ALL_SNAPSHOTS_RS_ERR           = 20143
    MSG_SER_THRD_DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG_ERR  = 20145
    MSG_SER_THRD_DVOL_DELETE_TARGET_RS_ERR                   = 20179
    MSG_THRD_CMS_DGCOM_REPORT_NODE_STATUS                    = 21001
    MSG_CMS_CMS_STOP_CMS                                     = 27001
    MSG_CMS_CMS_STOP_CMS_SUC                                 = 28001
    MSG_CMS_CMS_STOP_CMS_ERR                                 = 29001

    @property
    def desc(self):
        """Return a verbose description of what this message does."""
        return {
             3000: "Add User",
             3001: "Create",
             3005: "Configure Email Settings",
             3006: "Create Disk",
             3007: "Delete Disk",
             3008: "Resize Disk",
             3009: "Migrate",
             3011: "EMAIL_CONFIG_LIST",
             3013: "Start",
             3015: "Add License Key",
             3016: "LICENSE_LIST",
             3017: "DVOL_LIST_PLUN",
             3018: "DVOL_LIST_RECOVERY_PLAN",
             3019: "Update Recovery Plan",
             3022: "Delete User",
             3029: "Register",
             3030: "Unregister",
             3031: "Delete Protection Group",
             3032: "Failover",
             3033: "Failback Resync",
             3034: "Create Manual Checkpoint",
             3035: "Rollback",
             3036: "LIST_DVOL_SNAP",
             3037: "Edit Checkpoint Period",
             3038: "Create Test-Failover Image",
             3039: "Stop",
             3040: "CMS_LIST",
             3041: "Delete Test-Failover Image",
             3042: "Claim",
             3044: "USER_LIST",
             3045: "Set User Password",
             3049: "Repair Storage",
             3068: "Update Recovery Group",
             3069: "Convert To Local Cache",
             3070: "Remove VM From PG",
             3072: "DVOL_LIST_TARGETS",
             3073: "Set WAN Throttle",
             3074: "Convert To Local Replica",
             3075: "List software build version",
             3076: "Register SRN Peers",
             3077: "LIST_PEER_SRN",
             3079: "Unclaim",
             3080: "Unregister SRN Peers",
             3082: "Resize Snapshot Pool",
             3084: "Resize Snapshot Pool",
             3085: "Resize Primary Storage",
             3086: "Install LRA",
             3087: "Install Makestub",
             3088: "Convert In-Band To Local Boot",
             3089: "Add VMs To PG",
             3090: "Schedule Snapshot",
             4000: "Add User",
             4001: "Create",
             4005: "Configure Email Settings",
             4006: "Create Disk",
             4007: "Delete Disk",
             4008: "Resize Disk",
             4009: "Migrate",
             4011: "EMAIL_CONFIG_LIST",
             4013: "Start",
             4015: "Add License Key",
             4016: "LICENSE_LIST",
             4017: "DVOL_LIST_PLUN",
             4018: "DVOL_LIST_RECOVERY_PLAN",
             4019: "Update Recovery Plan",
             4022: "Delete User",
             4029: "Register",
             4030: "Unregister",
             4031: "Delete Protection Group",
             4032: "Failover",
             4033: "Failback Resync",
             4034: "Create Manual Checkpoint",
             4035: "Rollback",
             4036: "LIST_DVOL_SNAP",
             4037: "Edit Checkpoint Period",
             4038: "Create Test-Failover Image",
             4039: "Stop",
             4040: "CMS_LIST",
             4041: "Delete Test-Failover Image",
             4042: "Claim",
             4044: "USER_LIST",
             4045: "Set User Password",
             4049: "Repair Storage",
             4068: "Update Recovery Group",
             4069: "Convert To Local Cache",
             4070: "Remove VM From PG",
             4072: "DVOL_LIST_TARGETS",
             4073: "Set WAN Throttle",
             4074: "Convert To Local Replica",
             4075: "List software build version",
             4076: "Register SRN Peers",
             4077: "LIST_PEER_SRN",
             4079: "Unclaim",
             4080: "Unregister SRN Peers",
             4082: "Resize Snapshot Pool",
             4084: "Resize Snapshot Pool",
             4085: "Resize Primary Storage",
             4086: "Install LRA",
             4087: "Install Makestub",
             4088: "Convert In-Band To Local Boot",
             4089: "Add VMs To PG",
             4090: "Schedule Snapshot",
             5000: "Add User",
             5001: "Create",
             5005: "Configure Email Settings",
             5006: "Create Disk",
             5007: "Delete Disk",
             5008: "Resize Disk",
             5009: "Migrate",
             5011: "EMAIL_CONFIG_LIST",
             5013: "Start",
             5015: "Add License Key",
             5016: "LICENSE_LIST",
             5017: "DVOL_LIST_PLUN",
             5018: "DVOL_LIST_RECOVERY_PLAN",
             5019: "Update Recovery Plan",
             5022: "Delete User",
             5029: "Register",
             5030: "Unregister",
             5031: "Delete Protection Group",
             5032: "Failover",
             5033: "Failback Resync",
             5034: "Create Manual Checkpoint",
             5035: "Rollback",
             5036: "LIST_DVOL_SNAP",
             5037: "Edit Checkpoint Period",
             5038: "Create Test-Failover Image",
             5039: "Stop",
             5040: "CMS_LIST",
             5041: "Delete Test-Failover Image",
             5042: "Claim",
             5044: "USER_LIST",
             5045: "Set User Password",
             5049: "Repair Storage",
             5068: "Update Recovery Group",
             5069: "Convert To Local Cache",
             5070: "Remove VM From PG",
             5072: "DVOL_LIST_TARGETS",
             5073: "Set WAN Throttle",
             5074: "Convert To Local Replica",
             5075: "List software build version",
             5076: "Register SRN Peers",
             5077: "LIST_PEER_SRN",
             5079: "Unclaim",
             5080: "Unregister SRN Peers",
             5082: "Resize Snapshot Pool",
             5084: "Resize Snapshot Pool",
             5085: "Resize Primary Storage",
             5086: "Install LRA",
             5087: "Install Makestub",
             5088: "Convert In-Band To Local Boot",
             5089: "Add VMs To PG",
             5090: "Schedule Snapshot",
             6001: "Create",
             6002: "LIST_DVOL_PROP",
             6004: "Convert To Local Cache",
             6005: "Convert To Local Replica",
             6013: "Migrate",
             6028: "DVOL_SET_RESYNC_PERIOD",
             6032: "Delete Protection Group",
             6033: "Failover",
             6034: "Failback Resync",
             6035: "DVOL_FAILBACK_STOP_OLD_MASTER",
             6038: "Unregister",
             6039: "Create Manual Checkpoint",
             6040: "Rollback",
             6041: "LIST_DVOL_SNAP",
             6043: "Edit Checkpoint Period",
             6044: "Create Test-Failover Image",
             6048: "UPDATE_CMS",
             6051: "Delete Test-Failover Image",
             6053: "Claim",
             6067: "Repair Storage",
             6079: "Create Disk",
             6080: "Delete Disk",
             6081: "Resize Disk",
             6082: "DVOL_LIST_PLUN",
             6085: "DVOL_ADD_TARGET",
             6086: "Remove VM From PG",
             6088: "DVOL_LIST_RECOVERY_PLAN",
             6089: "Update Recovery Plan",
             6090: "Update Recovery Group",
             6091: "DVOL_LIST_TARGETS",
             6093: "Set WAN Throttle",
             6095: "Unclaim",
             6096: "Resize Snapshot Pool",
             6097: "Resize Snapshot Pool",
             6098: "Resize Primary Storage",
             6099: "Install LRA",
             6100: "Install Makestub",
             6101: "Convert In-Band To Local Boot",
             6102: "SRN_ADD_PEER_SRN",
             6103: "SRN_REMOVE_PEER_SRN",
             6104: "Add VMs To PG",
             6105: "Schedule Snapshot",
             7001: "Create",
             7002: "LIST_DVOL_PROP",
             7004: "Convert To Local Cache",
             7005: "Convert To Local Replica",
             7013: "Migrate",
             7028: "DVOL_SET_RESYNC_PERIOD",
             7032: "Delete Protection Group",
             7033: "Failover",
             7034: "Failback Resync",
             7035: "DVOL_FAILBACK_STOP_OLD_MASTER",
             7038: "Unregister",
             7039: "Create Manual Checkpoint",
             7040: "Rollback",
             7041: "LIST_DVOL_SNAP",
             7043: "Edit Checkpoint Period",
             7044: "Create Test-Failover Image",
             7048: "UPDATE_CMS",
             7051: "Delete Test-Failover Image",
             7053: "Claim",
             7067: "Repair Storage",
             7079: "Create Disk",
             7080: "Delete Disk",
             7081: "Resize Disk",
             7082: "DVOL_LIST_PLUN",
             7085: "DVOL_ADD_TARGET",
             7086: "Remove VM From PG",
             7088: "DVOL_LIST_RECOVERY_PLAN",
             7089: "Update Recovery Plan",
             7090: "Update Recovery Group",
             7091: "DVOL_LIST_TARGETS",
             7093: "Set WAN Throttle",
             7095: "Unclaim",
             7096: "Resize Snapshot Pool",
             7097: "Resize Snapshot Pool",
             7098: "Resize Primary Storage",
             7099: "Install LRA",
             7100: "Install Makestub",
             7101: "Convert In-Band To Local Boot",
             7102: "SRN_ADD_PEER_SRN",
             7103: "SRN_REMOVE_PEER_SRN",
             7104: "Add VMs To PG",
             7105: "Schedule Snapshot",
             8001: "Create",
             8002: "LIST_DVOL_PROP",
             8004: "Convert To Local Cache",
             8005: "Convert To Local Replica",
             8013: "Migrate",
             8028: "DVOL_SET_RESYNC_PERIOD",
             8032: "Delete Protection Group",
             8033: "Failover",
             8034: "Failback Resync",
             8035: "DVOL_FAILBACK_STOP_OLD_MASTER",
             8038: "Unregister",
             8039: "Create Manual Checkpoint",
             8040: "Rollback",
             8041: "LIST_DVOL_SNAP",
             8043: "Edit Checkpoint Period",
             8044: "Create Test-Failover Image",
             8048: "UPDATE_CMS",
             8051: "Delete Test-Failover Image",
             8053: "Claim",
             8067: "Repair Storage",
             8079: "Create Disk",
             8080: "Delete Disk",
             8081: "Resize Disk",
             8082: "DVOL_LIST_PLUN",
             8085: "DVOL_ADD_TARGET",
             8086: "Remove VM From PG",
             8088: "DVOL_LIST_RECOVERY_PLAN",
             8089: "Update Recovery Plan",
             8090: "Update Recovery Group",
             8091: "DVOL_LIST_TARGETS",
             8093: "Set WAN Throttle",
             8095: "Unclaim",
             8096: "Resize Snapshot Pool",
             8097: "Resize Snapshot Pool",
             8098: "Resize Primary Storage",
             8099: "Install LRA",
             8100: "Install Makestub",
             8101: "Convert In-Band To Local Boot",
             8102: "SRN_ADD_PEER_SRN",
             8103: "SRN_REMOVE_PEER_SRN",
             8104: "Add VMs To PG",
             8105: "Schedule Snapshot",
             9005: "DVOL_SET_ERROR",
            12002: "CREATE_DVOL_LEG",
            12004: "Convert To Local Cache",
            12005: "Convert To Local Replica",
            12006: "START_DVOL_LEG",
            12007: "STOP_DVOL_LEG",
            12012: "TRANS_AUTH_DVOL",
            12022: "CREATE_PLUN_RS",
            12024: "Delete Disk",
            12026: "Resize Disk",
            12030: "DVOL_SET_RESYNC_PERIOD_LEG",
            12035: "DVOL_RESIZE_DISKS_RS",
            12036: "DVOL_DELETE_LEG",
            12037: "DVOL_ROLLBACK_RS",
            12038: "DVOL_SNAPSHOT_RS",
            12040: "DVOL_DELETE_OLD_DISKS_LEG",
            12043: "DVOL_FAILBACK_RS",
            12056: "DVOL_SBD_STOP_SYNC_RS",
            12064: "DVOL_SET_SNAPSHOT_PERIOD_LEG",
            12066: "CREATE_TARGET_RS",
            12069: "DVOL_SNAPSHOT_SYNC",
            12070: "DVOL_SNAPSHOT_SYNC_RS",
            12073: "DVOL_DESTROY_RS",
            12079: "DVOL_STORAGE_REPAIR_RS",
            12081: "DVOL_LIST_PROP_RS",
            12082: "RECONSTITUTE_DVOLS",
            12086: "DVOL_RESERVE_SPACE_FOR_BACKUP_RS",
            12087: "DVOL_RELEASE_SPACE_FOR_BACKUP_RS",
            12088: "DVOL_ADD_TARGET_RS",
            12089: "DVOL_DELETE_TARGET_RS",
            12090: "DVOL_RESIZE_PRIMARY_RS",
            12091: "DVOL_RESIZE_SNAPSHOT_DEV_RS",
            12092: "DVOL_CREATE_RECOVERY_PLAN_RS",
            12093: "DVOL_PROVISION_STUBS_RS",
            12097: "DVOL_INVALID_ALL_SNAPSHOTS_RS",
            12098: "DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG",
            13002: "CREATE_DVOL_LEG",
            13004: "Convert To Local Cache",
            13005: "Convert To Local Replica",
            13006: "START_DVOL_LEG",
            13007: "STOP_DVOL_LEG",
            13012: "TRANS_AUTH_DVOL",
            13022: "CREATE_PLUN_RS",
            13024: "Delete Disk",
            13026: "Resize Disk",
            13030: "DVOL_SET_RESYNC_PERIOD_LEG",
            13035: "DVOL_RESIZE_DISKS_RS",
            13036: "DVOL_DELETE_LEG",
            13037: "DVOL_ROLLBACK_RS",
            13038: "DVOL_SNAPSHOT_RS",
            13040: "DVOL_DELETE_OLD_DISKS_LEG",
            13043: "DVOL_FAILBACK_RS",
            13056: "DVOL_SBD_STOP_SYNC_RS",
            13064: "DVOL_SET_SNAPSHOT_PERIOD_LEG",
            13066: "CREATE_TARGET_RS",
            13069: "DVOL_SNAPSHOT_SYNC",
            13070: "DVOL_SNAPSHOT_SYNC_RS",
            13073: "DVOL_DESTROY_RS",
            13079: "DVOL_STORAGE_REPAIR_RS",
            13081: "DVOL_LIST_PROP_RS",
            13086: "DVOL_RESERVE_SPACE_FOR_BACKUP_RS",
            13087: "DVOL_RELEASE_SPACE_FOR_BACKUP_RS",
            13088: "DVOL_ADD_TARGET_RS",
            13089: "DVOL_DELETE_TARGET_RS",
            13090: "DVOL_RESIZE_PRIMARY_RS",
            13091: "DVOL_RESIZE_SNAPSHOT_DEV_RS",
            13092: "DVOL_CREATE_RECOVERY_PLAN_RS",
            13093: "DVOL_PROVISION_STUBS_RS",
            13097: "DVOL_INVALID_ALL_SNAPSHOTS_RS",
            13098: "DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG",
            14002: "CREATE_DVOL_LEG",
            14004: "Convert To Local Cache",
            14005: "Convert To Local Replica",
            14006: "START_DVOL_LEG",
            14007: "STOP_DVOL_LEG",
            14012: "TRANS_AUTH_DVOL",
            14022: "CREATE_PLUN_RS",
            14024: "Delete Disk",
            14026: "Resize Disk",
            14030: "DVOL_SET_RESYNC_PERIOD_LEG",
            14035: "DVOL_RESIZE_DISKS_RS",
            14036: "DVOL_DELETE_LEG",
            14037: "DVOL_ROLLBACK_RS",
            14038: "DVOL_SNAPSHOT_RS",
            14040: "DVOL_DELETE_OLD_DISKS_LEG",
            14043: "DVOL_FAILBACK_RS",
            14056: "DVOL_SBD_STOP_SYNC_RS",
            14064: "DVOL_SET_SNAPSHOT_PERIOD_LEG",
            14066: "CREATE_TARGET_RS",
            14069: "DVOL_SNAPSHOT_SYNC",
            14070: "DVOL_SNAPSHOT_SYNC_RS",
            14073: "DVOL_DESTROY_RS",
            14079: "DVOL_STORAGE_REPAIR_RS",
            14081: "DVOL_LIST_PROP_RS",
            14086: "DVOL_RESERVE_SPACE_FOR_BACKUP_RS",
            14087: "DVOL_RELEASE_SPACE_FOR_BACKUP_RS",
            14088: "DVOL_ADD_TARGET_RS",
            14089: "DVOL_DELETE_TARGET_RS",
            14090: "DVOL_RESIZE_PRIMARY_RS",
            14091: "DVOL_RESIZE_SNAPSHOT_DEV_RS",
            14092: "DVOL_CREATE_RECOVERY_PLAN_RS",
            14093: "DVOL_PROVISION_STUBS_RS",
            14097: "DVOL_INVALID_ALL_SNAPSHOTS_RS",
            14098: "DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG",
            15001: "CREATE_DVOL_CMS",
            15002: "CREATE_DVOL_LEG",
            15006: "START_DVOL_LEG",
            15007: "STOP_DVOL_LEG",
            15008: "Convert To Local Cache",
            15009: "DVOL_CONVERT_COW_TO_ROW_RS",
            15010: "LIST_DVOL_PROP",
            15011: "Convert To Local Replica",
            15012: "DVOL_CONVERT_ROW_TO_COW_RS",
            15013: "Migrate",
            15014: "TRANS_AUTH_DVOL",
            15021: "SYNC_DVOL",
            15028: "DVOL_START_TGT",
            15033: "Create Disk",
            15034: "CREATE_PLUN_RS",
            15036: "SITE_REGISTER_LISTEN",
            15037: "SITE_REGISTER_SEND",
            15038: "SITE_UNREGISTER_LISTEN",
            15039: "SITE_UNREGISTER_SEND",
            15042: "DVOL_SBD_STOP_SYNC_RS",
            15049: "TIMER_REQUEST",
            15050: "SCHEDULE_EVENT",
            15053: "DVOL_SET_RESYNC_PERIOD",
            15054: "DVOL_SET_RESYNC_PERIOD_LEG",
            15063: "DVOL_DELETE_LEG",
            15064: "DVOL_RECONSTITUTE_MS",
            15065: "DVOL_ROLLBACK_RS",
            15067: "DVOL_RECONSTITUTE_RS",
            15068: "Update Recovery Group",
            15070: "DVOL_SNAPSHOT_RS",
            15071: "Delete Protection Group",
            15074: "DVOL_DELETE_OLD_DISKS_LEG",
            15075: "DVOL_SNAP_RS",
            15076: "Create Manual Checkpoint",
            15077: "Rollback",
            15078: "Create Test-Failover Image",
            15079: "LIST_DVOL_SNAP",
            15080: "Failover",
            15081: "Failback Resync",
            15082: "DVOL_FAILBACK_RS",
            15083: "DVOL_FAILBACK_STOP_OLD_MASTER",
            15084: "START_DVOL_MANAGER",
            15094: "DVOL_SBD_WAIT_FOR_SBD_ROLE",
            15097: "DVOL_PERIODIC_SNAPSHOT",
            15098: "DVOL_SCHEDULED_SNAPSHOT",
            15102: "DVOL_RESIZE_DISKS",
            15105: "Edit Checkpoint Period",
            15106: "DVOL_SET_SNAPSHOT_PERIOD_LEG",
            15110: "DVOL_SNAPSHOT_SYNC",
            15111: "DVOL_SNAPSHOT_SYNC_RS",
            15113: "TIMER_DESTROY_DVOL_TIMERS",
            15114: "DESTROY_SCHEDULED_EVENTS",
            15119: "DVOL_MANAGER_SHUTDOWN",
            15120: "DVOL_DESTROY_RS",
            15122: "DVOL_RESIZE_DISKS_RS",
            15123: "DVOL_STOP_ALL_TIMERS",
            15125: "DVOL_STOP_TARGET",
            15131: "Claim",
            15139: "DVOL_STOP",
            15145: "Repair Storage",
            15146: "DVOL_STORAGE_REPAIR_RS",
            15148: "DVOL_LIST_PROP_RS",
            15153: "Delete Test-Failover Image",
            15158: "DVOL_RESERVE_SPACE_FOR_BACKUP_RS",
            15159: "DVOL_RELEASE_SPACE_FOR_BACKUP_RS",
            15166: "Delete Disk",
            15167: "Delete Disk",
            15168: "Resize Disk",
            15169: "Resize Disk",
            15170: "DVOL_LIST_PLUN",
            15172: "CREATE_TARGET_RS",
            15173: "DVOL_LIST_RECOVERY_PLAN",
            15174: "Update Recovery Plan",
            15175: "MONITOR_TEST_FAILOVER_QUOTA",
            15176: "DVOL_ADD_TARGET",
            15177: "DVOL_ADD_TARGET_RS",
            15178: "Remove VM From PG",
            15179: "DVOL_DELETE_TARGET_RS",
            15180: "DVOL_LIST_TARGETS",
            15181: "Set WAN Throttle",
            15183: "Unclaim",
            15184: "Resize Snapshot Pool",
            15185: "Resize Snapshot Pool",
            15186: "Resize Primary Storage",
            15187: "DVOL_RESIZE_PRIMARY_RS",
            15188: "Install LRA",
            15189: "Install Makestub",
            15190: "Convert In-Band To Local Boot",
            15192: "DVOL_RESIZE_SNAPSHOT_DEV_RS",
            15193: "DVOL_CREATE_RECOVERY_PLAN_RS",
            15194: "DVOL_PROVISION_STUBS_RS",
            15196: "SRN_ADD_PEER_SRN",
            15197: "SRN_REMOVE_PEER_SRN",
            15199: "Add VMs To PG",
            15201: "DVOL_INVALID_ALL_SNAPSHOTS_RS",
            15202: "Schedule Snapshot",
            15203: "DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG",
            16001: "CREATE_DVOL_CMS",
            16002: "CREATE_DVOL_LEG",
            16006: "START_DVOL_LEG",
            16007: "STOP_DVOL_LEG",
            16008: "Convert To Local Cache",
            16009: "DVOL_CONVERT_COW_TO_ROW_RS",
            16010: "LIST_DVOL_PROP",
            16011: "Convert To Local Replica",
            16012: "DVOL_CONVERT_ROW_TO_COW_RS",
            16013: "Migrate",
            16014: "TRANS_AUTH_DVOL",
            16028: "DVOL_START_TGT",
            16033: "Create Disk",
            16034: "CREATE_PLUN_RS",
            16036: "SITE_REGISTER_LISTEN",
            16037: "SITE_REGISTER_SEND",
            16038: "SITE_UNREGISTER_LISTEN",
            16039: "SITE_UNREGISTER_SEND",
            16042: "DVOL_SBD_STOP_SYNC_RS",
            16053: "DVOL_SET_RESYNC_PERIOD",
            16054: "DVOL_SET_RESYNC_PERIOD_LEG",
            16063: "DVOL_DELETE_LEG",
            16064: "DVOL_RECONSTITUTE_MS",
            16065: "DVOL_ROLLBACK_RS",
            16067: "DVOL_RECONSTITUTE_RS",
            16068: "Update Recovery Group",
            16070: "DVOL_SNAPSHOT_RS",
            16071: "Delete Protection Group",
            16074: "DVOL_DELETE_OLD_DISKS_LEG",
            16075: "DVOL_SNAP_RS",
            16076: "Create Manual Checkpoint",
            16077: "Rollback",
            16078: "Create Test-Failover Image",
            16079: "LIST_DVOL_SNAP",
            16080: "Failover",
            16081: "Failback Resync",
            16082: "DVOL_FAILBACK_RS",
            16083: "DVOL_FAILBACK_STOP_OLD_MASTER",
            16084: "START_DVOL_MANAGER",
            16094: "DVOL_SBD_WAIT_FOR_SBD_ROLE",
            16102: "DVOL_RESIZE_DISKS",
            16105: "Edit Checkpoint Period",
            16106: "DVOL_SET_SNAPSHOT_PERIOD_LEG",
            16110: "DVOL_SNAPSHOT_SYNC",
            16111: "DVOL_SNAPSHOT_SYNC_RS",
            16119: "DVOL_MANAGER_SHUTDOWN",
            16120: "DVOL_DESTROY_RS",
            16122: "DVOL_RESIZE_DISKS_RS",
            16123: "DVOL_STOP_ALL_TIMERS",
            16125: "DVOL_STOP_TARGET",
            16131: "Claim",
            16139: "DVOL_STOP",
            16145: "Repair Storage",
            16146: "DVOL_STORAGE_REPAIR_RS",
            16148: "DVOL_LIST_PROP_RS",
            16153: "Delete Test-Failover Image",
            16158: "DVOL_RESERVE_SPACE_FOR_BACKUP_RS",
            16159: "DVOL_RELEASE_SPACE_FOR_BACKUP_RS",
            16166: "Delete Disk",
            16167: "Delete Disk",
            16168: "Resize Disk",
            16169: "Resize Disk",
            16170: "DVOL_LIST_PLUN",
            16172: "CREATE_TARGET_RS",
            16173: "DVOL_LIST_RECOVERY_PLAN",
            16174: "Update Recovery Plan",
            16175: "MONITOR_TEST_FAILOVER_QUOTA",
            16176: "DVOL_ADD_TARGET",
            16177: "DVOL_ADD_TARGET_RS",
            16178: "Remove VM From PG",
            16179: "DVOL_DELETE_TARGET_RS",
            16180: "DVOL_LIST_TARGETS",
            16181: "Set WAN Throttle",
            16183: "Unclaim",
            16184: "Resize Snapshot Pool",
            16185: "Resize Snapshot Pool",
            16186: "Resize Primary Storage",
            16187: "DVOL_RESIZE_PRIMARY_RS",
            16188: "Install LRA",
            16189: "Install Makestub",
            16190: "Convert In-Band To Local Boot",
            16192: "DVOL_RESIZE_SNAPSHOT_DEV_RS",
            16193: "DVOL_CREATE_RECOVERY_PLAN_RS",
            16194: "DVOL_PROVISION_STUBS_RS",
            16196: "SRN_ADD_PEER_SRN",
            16197: "SRN_REMOVE_PEER_SRN",
            16199: "Add VMs To PG",
            16201: "DVOL_INVALID_ALL_SNAPSHOTS_RS",
            16202: "Schedule Snapshot",
            16203: "DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG",
            17001: "CREATE_DVOL_CMS",
            17002: "CREATE_DVOL_LEG",
            17006: "START_DVOL_LEG",
            17007: "STOP_DVOL_LEG",
            17008: "Convert To Local Cache",
            17009: "DVOL_CONVERT_COW_TO_ROW_RS",
            17010: "LIST_DVOL_PROP",
            17011: "Convert To Local Replica",
            17012: "DVOL_CONVERT_ROW_TO_COW_RS",
            17013: "Migrate",
            17014: "TRANS_AUTH_DVOL",
            17021: "SYNC_DVOL",
            17028: "DVOL_START_TGT",
            17033: "Create Disk",
            17034: "CREATE_PLUN_RS",
            17036: "SITE_REGISTER_LISTEN",
            17037: "SITE_REGISTER_SEND",
            17038: "SITE_UNREGISTER_LISTEN",
            17039: "SITE_UNREGISTER_SEND",
            17042: "DVOL_SBD_STOP_SYNC_RS",
            17053: "DVOL_SET_RESYNC_PERIOD",
            17054: "DVOL_SET_RESYNC_PERIOD_LEG",
            17063: "DVOL_DELETE_LEG",
            17064: "DVOL_RECONSTITUTE_MS",
            17065: "DVOL_ROLLBACK_RS",
            17067: "DVOL_RECONSTITUTE_RS",
            17068: "Update Recovery Group",
            17070: "DVOL_SNAPSHOT_RS",
            17071: "Delete Protection Group",
            17074: "DVOL_DELETE_OLD_DISKS_LEG",
            17075: "DVOL_SNAP_RS",
            17076: "Create Manual Checkpoint",
            17077: "Rollback",
            17078: "Create Test-Failover Image",
            17079: "LIST_DVOL_SNAP",
            17080: "Failover",
            17081: "Failback Resync",
            17082: "DVOL_FAILBACK_RS",
            17083: "DVOL_FAILBACK_STOP_OLD_MASTER",
            17084: "START_DVOL_MANAGER",
            17094: "DVOL_SBD_WAIT_FOR_SBD_ROLE",
            17102: "DVOL_RESIZE_DISKS",
            17105: "Edit Checkpoint Period",
            17106: "DVOL_SET_SNAPSHOT_PERIOD_LEG",
            17110: "DVOL_SNAPSHOT_SYNC",
            17111: "DVOL_SNAPSHOT_SYNC_RS",
            17119: "DVOL_MANAGER_SHUTDOWN",
            17120: "DVOL_DESTROY_RS",
            17122: "DVOL_RESIZE_DISKS_RS",
            17123: "DVOL_STOP_ALL_TIMERS",
            17125: "DVOL_STOP_TARGET",
            17131: "Claim",
            17139: "DVOL_STOP",
            17145: "Repair Storage",
            17146: "DVOL_STORAGE_REPAIR_RS",
            17148: "DVOL_LIST_PROP_RS",
            17153: "Delete Test-Failover Image",
            17158: "DVOL_RESERVE_SPACE_FOR_BACKUP_RS",
            17159: "DVOL_RELEASE_SPACE_FOR_BACKUP_RS",
            17166: "Delete Disk",
            17167: "Delete Disk",
            17168: "Resize Disk",
            17169: "Resize Disk",
            17170: "DVOL_LIST_PLUN",
            17172: "CREATE_TARGET_RS",
            17173: "DVOL_LIST_RECOVERY_PLAN",
            17174: "Update Recovery Plan",
            17175: "MONITOR_TEST_FAILOVER_QUOTA",
            17176: "DVOL_ADD_TARGET",
            17177: "DVOL_ADD_TARGET_RS",
            17178: "Remove VM From PG",
            17179: "DVOL_DELETE_TARGET_RS",
            17180: "DVOL_LIST_TARGETS",
            17181: "Set WAN Throttle",
            17183: "Unclaim",
            17184: "Resize Snapshot Pool",
            17185: "Resize Snapshot Pool",
            17186: "Resize Primary Storage",
            17187: "DVOL_RESIZE_PRIMARY_RS",
            17188: "Install LRA",
            17189: "Install Makestub",
            17190: "Convert In-Band To Local Boot",
            17192: "DVOL_RESIZE_SNAPSHOT_DEV_RS",
            17193: "DVOL_CREATE_RECOVERY_PLAN_RS",
            17194: "DVOL_PROVISION_STUBS_RS",
            17196: "SRN_ADD_PEER_SRN",
            17197: "SRN_REMOVE_PEER_SRN",
            17199: "Add VMs To PG",
            17201: "DVOL_INVALID_ALL_SNAPSHOTS_RS",
            17202: "Schedule Snapshot",
            17203: "DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG",
            18002: "CREATE_DVOL_LEG",
            18004: "STOP",
            18006: "START_DVOL_LEG",
            18007: "STOP_DVOL_LEG",
            18008: "Convert To Local Cache",
            18009: "DVOL_CONVERT_COW_TO_ROW_RS",
            18011: "Convert To Local Replica",
            18012: "DVOL_CONVERT_ROW_TO_COW_RS",
            18013: "Migrate",
            18014: "TRANS_AUTH_DVOL",
            18018: "SYNC_DVOL",
            18025: "DVOL_START_TGT",
            18028: "DVOL_MANAGER_SHUTDOWN",
            18030: "CREATE_PLUN_RS",
            18031: "SITE_REGISTER_LISTEN",
            18032: "SITE_REGISTER_SEND",
            18033: "SITE_UNREGISTER_LISTEN",
            18034: "SITE_UNREGISTER_SEND",
            18037: "DVOL_SBD_STOP_SYNC_RS",
            18040: "DVOL_SBD_WAIT_FOR_SBD_ROLE",
            18043: "TIMER_REQUEST",
            18044: "SCHEDULE_EVENT",
            18046: "DVOL_SET_RESYNC_PERIOD_LEG",
            18053: "DVOL_DELETE_LEG",
            18054: "DVOL_ROLLBACK_RS",
            18055: "DVOL_SNAPSHOT_RS",
            18057: "DVOL_DELETE_OLD_DISKS_LEG",
            18058: "DVOL_SNAP_RS",
            18059: "DVOL_PERIODIC_SNAPSHOT",
            18060: "Rollback",
            18061: "DVOL_FAILBACK_RS",
            18062: "DVOL_FAILBACK_STOP_OLD_MASTER",
            18063: "Failback Resync",
            18066: "DVOL_DELETE_SNAPSHOTS",
            18068: "DVOL_STOP_TARGET",
            18075: "DVOL_RESIZE_DISKS",
            18076: "DVOL_RESIZE_DISKS_RS",
            18083: "DVOL_STOP_ALL_TIMERS",
            18085: "DVOL_SET_SNAPSHOT_PERIOD_LEG",
            18092: "DVOL_SNAPSHOT_SYNC_RS",
            18095: "TIMER_DESTROY_DVOL_TIMERS",
            18096: "DESTROY_SCHEDULED_EVENTS",
            18099: "DGCOM_REPORT_NODE_STATUS",
            18101: "DVOL_DESTROY_RS",
            18102: "DVOL_SNAPSHOT",
            18103: "DVOL_SET_ERROR",
            18114: "DVOL_STOP",
            18116: "Repair Storage",
            18117: "DVOL_STORAGE_REPAIR_RS",
            18119: "DVOL_LIST_PROP_RS",
            18123: "DVOL_RESERVE_SPACE_FOR_BACKUP_RS",
            18124: "DVOL_RELEASE_SPACE_FOR_BACKUP_RS",
            18129: "Delete Disk",
            18130: "Resize Disk",
            18133: "CREATE_TARGET_RS",
            18134: "MONITOR_TEST_FAILOVER_QUOTA",
            18135: "DVOL_ADD_TARGET_RS",
            18136: "DVOL_RESIZE_PRIMARY_RS",
            18137: "DVOL_RESIZE_SNAPSHOT_DEV_RS",
            18138: "DVOL_CREATE_RECOVERY_PLAN_RS",
            18139: "DVOL_PROVISION_STUBS_RS",
            18143: "DVOL_INVALID_ALL_SNAPSHOTS_RS",
            18144: "DVOL_SCHEDULED_SNAPSHOT",
            18145: "DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG",
            18146: "RECONSTITUTION_TIMER",
            18179: "DVOL_DELETE_TARGET_RS",
            19002: "CREATE_DVOL_LEG",
            19006: "START_DVOL_LEG",
            19007: "STOP_DVOL_LEG",
            19008: "Convert To Local Cache",
            19009: "DVOL_CONVERT_COW_TO_ROW_RS",
            19011: "Convert To Local Replica",
            19012: "DVOL_CONVERT_ROW_TO_COW_RS",
            19013: "Migrate",
            19014: "TRANS_AUTH_DVOL",
            19025: "DVOL_START_TGT",
            19030: "CREATE_PLUN_RS",
            19031: "SITE_REGISTER_LISTEN",
            19032: "SITE_REGISTER_SEND",
            19033: "SITE_UNREGISTER_LISTEN",
            19034: "SITE_UNREGISTER_SEND",
            19037: "DVOL_SBD_STOP_SYNC_RS",
            19040: "DVOL_SBD_WAIT_FOR_SBD_ROLE",
            19046: "DVOL_SET_RESYNC_PERIOD_LEG",
            19053: "DVOL_DELETE_LEG",
            19054: "DVOL_ROLLBACK_RS",
            19055: "DVOL_SNAPSHOT_RS",
            19057: "DVOL_DELETE_OLD_DISKS_LEG",
            19058: "DVOL_SNAP_RS",
            19060: "Rollback",
            19061: "DVOL_FAILBACK_RS",
            19062: "DVOL_FAILBACK_STOP_OLD_MASTER",
            19063: "Failback Resync",
            19066: "DVOL_DELETE_SNAPSHOTS",
            19068: "DVOL_STOP_TARGET",
            19075: "DVOL_RESIZE_DISKS",
            19076: "DVOL_RESIZE_DISKS_RS",
            19083: "DVOL_STOP_ALL_TIMERS",
            19085: "DVOL_SET_SNAPSHOT_PERIOD_LEG",
            19092: "DVOL_SNAPSHOT_SYNC_RS",
            19099: "DGCOM_REPORT_NODE_STATUS",
            19101: "DVOL_DESTROY_RS",
            19102: "DVOL_SNAPSHOT",
            19112: "Delete Test-Failover Image",
            19114: "DVOL_STOP",
            19116: "Repair Storage",
            19117: "DVOL_STORAGE_REPAIR_RS",
            19119: "DVOL_LIST_PROP_RS",
            19123: "DVOL_RESERVE_SPACE_FOR_BACKUP_RS",
            19124: "DVOL_RELEASE_SPACE_FOR_BACKUP_RS",
            19129: "Delete Disk",
            19130: "Resize Disk",
            19133: "CREATE_TARGET_RS",
            19135: "DVOL_ADD_TARGET_RS",
            19136: "DVOL_RESIZE_PRIMARY_RS",
            19137: "DVOL_RESIZE_SNAPSHOT_DEV_RS",
            19138: "DVOL_CREATE_RECOVERY_PLAN_RS",
            19139: "DVOL_PROVISION_STUBS_RS",
            19143: "DVOL_INVALID_ALL_SNAPSHOTS_RS",
            19145: "DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG",
            19179: "DVOL_DELETE_TARGET_RS",
            20002: "CREATE_DVOL_LEG",
            20006: "START_DVOL_LEG",
            20007: "STOP_DVOL_LEG",
            20008: "Convert To Local Cache",
            20009: "DVOL_CONVERT_COW_TO_ROW_RS",
            20011: "Convert To Local Replica",
            20012: "DVOL_CONVERT_ROW_TO_COW_RS",
            20013: "Migrate",
            20014: "TRANS_AUTH_DVOL",
            20025: "DVOL_START_TGT",
            20030: "CREATE_PLUN_RS",
            20031: "SITE_REGISTER_LISTEN",
            20032: "SITE_REGISTER_SEND",
            20033: "SITE_UNREGISTER_LISTEN",
            20034: "SITE_UNREGISTER_SEND",
            20037: "DVOL_SBD_STOP_SYNC_RS",
            20040: "DVOL_SBD_WAIT_FOR_SBD_ROLE",
            20046: "DVOL_SET_RESYNC_PERIOD_LEG",
            20053: "DVOL_DELETE_LEG",
            20054: "DVOL_ROLLBACK_RS",
            20055: "DVOL_SNAPSHOT_RS",
            20057: "DVOL_DELETE_OLD_DISKS_LEG",
            20058: "DVOL_SNAP_RS",
            20060: "Rollback",
            20061: "DVOL_FAILBACK_RS",
            20062: "DVOL_FAILBACK_STOP_OLD_MASTER",
            20063: "Failback Resync",
            20066: "DVOL_DELETE_SNAPSHOTS",
            20068: "DVOL_STOP_TARGET",
            20075: "DVOL_RESIZE_DISKS",
            20076: "DVOL_RESIZE_DISKS_RS",
            20083: "DVOL_STOP_ALL_TIMERS",
            20085: "DVOL_SET_SNAPSHOT_PERIOD_LEG",
            20092: "DVOL_SNAPSHOT_SYNC_RS",
            20099: "DGCOM_REPORT_NODE_STATUS",
            20101: "DVOL_DESTROY_RS",
            20102: "DVOL_SNAPSHOT",
            20112: "Delete Test-Failover Image",
            20114: "DVOL_STOP",
            20116: "Repair Storage",
            20117: "DVOL_STORAGE_REPAIR_RS",
            20119: "DVOL_LIST_PROP_RS",
            20123: "DVOL_RESERVE_SPACE_FOR_BACKUP_RS",
            20124: "DVOL_RELEASE_SPACE_FOR_BACKUP_RS",
            20129: "Delete Disk",
            20130: "Resize Disk",
            20133: "CREATE_TARGET_RS",
            20135: "DVOL_ADD_TARGET_RS",
            20136: "DVOL_RESIZE_PRIMARY_RS",
            20137: "DVOL_RESIZE_SNAPSHOT_DEV_RS",
            20138: "DVOL_CREATE_RECOVERY_PLAN_RS",
            20139: "DVOL_PROVISION_STUBS_RS",
            20143: "DVOL_INVALID_ALL_SNAPSHOTS_RS",
            20145: "DVOL_SET_SCHEDULED_SNAPSHOT_PERIOD_LEG",
            20179: "DVOL_DELETE_TARGET_RS",
            21001: "DGCOM_REPORT_NODE_STATUS",
            27001: "STOP_CMS",
            28001: "STOP_CMS",
            29001: "STOP_CMS",
        }[self._value_]

    @property
    def nbParams(self):
        """Return the expected number of params (msg.params[]) of this message."""
        return {
             3000:  3,
             3001: 40,
             3005:  7,
             3006:  4,
             3007:  3,
             3008:  4,
             3009:  2,
             3011:  0,
             3013:  1,
             3015:  1,
             3016:  0,
             3017:  1,
             3018:  2,
             3019:  4,
             3022:  1,
             3029:  7,
             3030:  1,
             3031:  1,
             3032:  3,
             3033:  5,
             3034:  3,
             3035:  3,
             3036:  2,
             3037:  2,
             3038:  5,
             3039:  1,
             3040:  0,
             3041:  2,
             3042:  3,
             3044:  0,
             3045:  3,
             3049:  2,
             3068:  3,
             3069:  3,
             3070:  2,
             3072:  2,
             3073:  2,
             3074:  4,
             3075:  0,
             3076:  4,
             3077:  1,
             3079:  3,
             3080:  2,
             3082:  3,
             3084:  2,
             3085:  2,
             3086:  8,
             3087:  7,
             3088:  5,
             3089: 25,
             3090:  4,
             4000:  1,
             4001:  1,
             4005:  0,
             4006:  2,
             4007:  2,
             4008:  2,
             4009:  1,
             4011:  7,
             4013:  0,
             4015:  1,
             4016:  4,
             4017:  0,
             4018:  0,
             4019:  0,
             4022:  1,
             4029:  1,
             4030:  1,
             4031:  1,
             4032:  1,
             4033:  2,
             4034:  1,
             4035:  2,
             4036:  1,
             4037:  1,
             4038:  1,
             4039:  1,
             4040:  2,
             4041:  1,
             4042:  1,
             4044:  0,
             4045:  1,
             4049:  2,
             4068:  1,
             4069:  1,
             4070:  2,
             4072:  0,
             4073:  1,
             4074:  1,
             4075:  1,
             4076:  2,
             4077:  2,
             4079:  1,
             4080:  2,
             4082:  1,
             4084:  1,
             4085:  1,
             4086:  1,
             4087:  1,
             4088:  1,
             4089:  2,
             4090:  1,
             5000:  2,
             5001:  2,
             5005:  2,
             5006:  3,
             5007:  3,
             5008:  3,
             5009:  2,
             5011:  2,
             5013:  2,
             5015:  2,
             5016:  2,
             5017:  2,
             5018:  2,
             5019:  2,
             5022:  2,
             5029:  2,
             5030:  2,
             5031:  2,
             5032:  2,
             5033:  2,
             5034:  2,
             5035:  2,
             5036:  2,
             5037:  2,
             5038:  2,
             5039:  2,
             5040:  2,
             5041:  2,
             5042:  2,
             5044:  2,
             5045:  2,
             5049:  2,
             5068:  2,
             5069:  2,
             5070:  3,
             5072:  2,
             5073:  2,
             5074:  2,
             5075:  2,
             5076:  2,
             5077:  0,
             5079:  2,
             5080:  2,
             5082:  2,
             5084:  2,
             5085:  2,
             5086:  3,
             5087:  3,
             5088:  3,
             5089:  3,
             5090:  2,
             6001: 51,
             6002:  1,
             6004:  3,
             6005:  4,
             6013:  2,
             6028:  2,
             6032:  2,
             6033:  3,
             6034:  5,
             6035:  5,
             6038:  1,
             6039:  3,
             6040:  3,
             6041:  2,
             6043:  2,
             6044:  5,
             6048:  0,
             6051:  2,
             6053:  3,
             6067:  2,
             6079:  5,
             6080:  3,
             6081:  4,
             6082:  1,
             6085:  0,
             6086:  2,
             6088:  2,
             6089:  4,
             6090:  3,
             6091:  2,
             6093:  2,
             6095:  3,
             6096:  3,
             6097:  2,
             6098:  2,
             6099:  8,
             6100:  7,
             6101:  5,
             6102:  4,
             6103:  4,
             6104: 25,
             6105:  4,
             7001:  1,
             7002: 23,
             7004:  1,
             7005:  1,
             7013:  1,
             7028:  1,
             7032:  1,
             7033:  1,
             7034:  2,
             7035:  5,
             7038:  1,
             7039:  1,
             7040:  2,
             7041:  1,
             7043:  1,
             7044:  1,
             7048:  0,
             7051:  1,
             7053:  1,
             7067:  2,
             7079:  2,
             7080:  2,
             7081:  2,
             7082:  0,
             7085:  0,
             7086:  2,
             7088:  0,
             7089:  0,
             7090:  1,
             7091:  0,
             7093:  1,
             7095:  1,
             7096:  1,
             7097:  1,
             7098:  1,
             7099:  1,
             7100:  1,
             7101:  1,
             7102:  2,
             7103:  2,
             7104:  2,
             7105:  1,
             8001:  2,
             8002:  2,
             8004:  2,
             8005:  2,
             8013:  2,
             8028:  2,
             8032:  2,
             8033:  2,
             8034:  2,
             8035:  2,
             8038:  2,
             8039:  2,
             8040:  2,
             8041:  2,
             8043:  2,
             8044:  2,
             8048:  2,
             8051:  2,
             8053:  2,
             8067:  2,
             8079:  3,
             8080:  3,
             8081:  3,
             8082:  2,
             8085:  0,
             8086:  3,
             8088:  2,
             8089:  2,
             8090:  2,
             8091:  2,
             8093:  2,
             8095:  2,
             8096:  2,
             8097:  2,
             8098:  2,
             8099:  3,
             8100:  3,
             8101:  3,
             8102:  2,
             8103:  2,
             8104:  3,
             8105:  2,
             9005:  3,
            12002: 52,
            12004:  3,
            12005:  4,
            12006:  1,
            12007:  2,
            12012:  4,
            12022:  4,
            12024:  3,
            12026:  4,
            12030:  2,
            12035:  2,
            12036:  1,
            12037:  2,
            12038:  7,
            12040:  0,
            12043:  2,
            12056:  1,
            12064:  3,
            12066:  8,
            12069:  1,
            12070:  2,
            12073:  1,
            12079:  2,
            12081:  1,
            12082:  1,
            12086:  2,
            12087:  2,
            12088:  0,
            12089:  2,
            12090:  3,
            12091:  2,
            12092:  4,
            12093: 15,
            12097:  1,
            12098:  4,
            13002:  2,
            13004:  1,
            13005:  1,
            13006:  1,
            13007:  1,
            13012:  1,
            13022:  2,
            13024:  2,
            13026:  2,
            13030:  1,
            13035:  1,
            13036:  1,
            13037:  1,
            13038:  1,
            13040:  0,
            13043:  1,
            13056:  1,
            13064:  1,
            13066:  2,
            13069:  2,
            13070:  1,
            13073:  1,
            13079:  2,
            13081: 23,
            13086:  1,
            13087:  1,
            13088:  0,
            13089:  2,
            13090:  1,
            13091:  1,
            13092:  1,
            13093:  2,
            13097:  0,
            13098:  1,
            14002:  2,
            14004:  2,
            14005:  2,
            14006:  2,
            14007:  2,
            14012:  2,
            14022:  3,
            14024:  3,
            14026:  3,
            14030:  2,
            14035:  2,
            14036:  2,
            14037:  2,
            14038:  2,
            14040:  0,
            14043:  2,
            14056:  2,
            14064:  2,
            14066:  3,
            14069:  2,
            14070:  2,
            14073:  2,
            14079:  2,
            14081:  2,
            14086:  2,
            14087:  2,
            14088:  0,
            14089:  3,
            14090:  2,
            14091:  2,
            14092:  2,
            14093:  2,
            14097:  2,
            14098:  2,
            15001: 51,
            15002: 52,
            15006:  1,
            15007:  2,
            15008:  3,
            15009:  3,
            15010:  1,
            15011:  4,
            15012:  0,
            15013:  2,
            15014:  4,
            15021:  2,
            15028:  1,
            15033:  5,
            15034:  4,
            15036:  2,
            15037:  2,
            15038:  2,
            15039:  2,
            15042:  1,
            15049:  2,
            15050:  3,
            15053:  2,
            15054:  2,
            15063:  1,
            15064:  3,
            15065:  2,
            15067:  3,
            15068:  3,
            15070:  7,
            15071:  2,
            15074:  0,
            15075:  0,
            15076:  3,
            15077:  3,
            15078:  5,
            15079:  2,
            15080:  3,
            15081:  5,
            15082:  2,
            15083:  5,
            15084:  1,
            15094:  3,
            15097:  1,
            15098:  2,
            15102:  2,
            15105:  2,
            15106:  3,
            15110:  1,
            15111:  2,
            15113:  1,
            15114:  1,
            15119:  3,
            15120:  1,
            15122:  2,
            15123:  1,
            15125:  1,
            15131:  3,
            15139:  1,
            15145:  2,
            15146:  2,
            15148:  1,
            15153:  2,
            15158:  2,
            15159:  2,
            15166:  3,
            15167:  3,
            15168:  4,
            15169:  4,
            15170:  1,
            15172:  8,
            15173:  2,
            15174:  4,
            15175:  1,
            15176:  0,
            15177:  0,
            15178:  2,
            15179:  2,
            15180:  2,
            15181:  2,
            15183:  3,
            15184:  3,
            15185:  2,
            15186:  2,
            15187:  3,
            15188:  8,
            15189:  7,
            15190:  5,
            15192:  2,
            15193:  4,
            15194: 15,
            15196:  4,
            15197:  4,
            15199: 25,
            15201:  1,
            15202:  4,
            15203:  4,
            16001:  1,
            16002:  2,
            16006:  1,
            16007:  1,
            16008:  1,
            16009:  1,
            16010: 23,
            16011:  1,
            16012:  0,
            16013:  1,
            16014:  1,
            16028:  1,
            16033:  2,
            16034:  2,
            16036:  0,
            16037:  0,
            16038:  0,
            16039:  0,
            16042:  1,
            16053:  1,
            16054:  1,
            16063:  1,
            16064:  1,
            16065:  1,
            16067:  1,
            16068:  1,
            16070:  1,
            16071:  1,
            16074:  0,
            16075:  0,
            16076:  1,
            16077:  2,
            16078:  1,
            16079:  1,
            16080:  1,
            16081:  2,
            16082:  1,
            16083:  5,
            16084:  1,
            16094:  1,
            16102:  1,
            16105:  1,
            16106:  1,
            16110:  2,
            16111:  1,
            16119:  2,
            16120:  1,
            16122:  1,
            16123:  1,
            16125:  1,
            16131:  1,
            16139:  0,
            16145:  2,
            16146:  2,
            16148: 23,
            16153:  1,
            16158:  1,
            16159:  1,
            16166:  2,
            16167:  2,
            16168:  2,
            16169:  2,
            16170:  0,
            16172:  2,
            16173:  0,
            16174:  0,
            16175:  0,
            16176:  0,
            16177:  0,
            16178:  2,
            16179:  2,
            16180:  0,
            16181:  1,
            16183:  1,
            16184:  1,
            16185:  1,
            16186:  1,
            16187:  1,
            16188:  1,
            16189:  1,
            16190:  1,
            16192:  1,
            16193:  1,
            16194:  2,
            16196:  2,
            16197:  2,
            16199:  2,
            16201:  0,
            16202:  1,
            16203:  1,
            17001:  2,
            17002:  2,
            17006:  2,
            17007:  2,
            17008:  2,
            17009:  2,
            17010:  2,
            17011:  2,
            17012:  0,
            17013:  2,
            17014:  2,
            17021:  0,
            17028:  2,
            17033:  3,
            17034:  3,
            17036:  0,
            17037:  0,
            17038:  0,
            17039:  0,
            17042:  2,
            17053:  2,
            17054:  2,
            17063:  2,
            17064:  2,
            17065:  2,
            17067:  2,
            17068:  2,
            17070:  2,
            17071:  2,
            17074:  0,
            17075:  0,
            17076:  2,
            17077:  2,
            17078:  2,
            17079:  2,
            17080:  2,
            17081:  2,
            17082:  2,
            17083:  2,
            17084:  2,
            17094:  2,
            17102:  2,
            17105:  2,
            17106:  2,
            17110:  2,
            17111:  2,
            17119:  2,
            17120:  2,
            17122:  2,
            17123:  2,
            17125:  2,
            17131:  2,
            17139:  0,
            17145:  2,
            17146:  2,
            17148:  2,
            17153:  2,
            17158:  2,
            17159:  2,
            17166:  3,
            17167:  3,
            17168:  3,
            17169:  3,
            17170:  2,
            17172:  3,
            17173:  2,
            17174:  2,
            17175:  0,
            17176:  0,
            17177:  0,
            17178:  3,
            17179:  3,
            17180:  2,
            17181:  2,
            17183:  2,
            17184:  2,
            17185:  2,
            17186:  2,
            17187:  2,
            17188:  3,
            17189:  3,
            17190:  3,
            17192:  2,
            17193:  2,
            17194:  2,
            17196:  2,
            17197:  2,
            17199:  3,
            17201:  2,
            17202:  2,
            17203:  2,
            18002: 52,
            18004:  0,
            18006:  1,
            18007:  2,
            18008:  3,
            18009:  3,
            18011:  4,
            18012:  0,
            18013:  2,
            18014:  4,
            18018:  2,
            18025:  1,
            18028:  3,
            18030:  4,
            18031:  2,
            18032:  2,
            18033:  2,
            18034:  2,
            18037:  1,
            18040:  3,
            18043:  2,
            18044:  3,
            18046:  2,
            18053:  1,
            18054:  2,
            18055:  7,
            18057:  0,
            18058:  0,
            18059:  1,
            18060:  3,
            18061:  2,
            18062:  5,
            18063:  5,
            18066:  0,
            18068:  1,
            18075:  2,
            18076:  2,
            18083:  1,
            18085:  3,
            18092:  2,
            18095:  1,
            18096:  1,
            18099:  4,
            18101:  1,
            18102:  2,
            18103:  3,
            18114:  1,
            18116:  2,
            18117:  2,
            18119:  1,
            18123:  2,
            18124:  2,
            18129:  3,
            18130:  4,
            18133:  8,
            18134:  1,
            18135:  0,
            18136:  3,
            18137:  2,
            18138:  4,
            18139: 15,
            18143:  1,
            18144:  2,
            18145:  4,
            18146:  0,
            18179:  2,
            19002:  2,
            19006:  1,
            19007:  1,
            19008:  1,
            19009:  1,
            19011:  1,
            19012:  0,
            19013:  1,
            19014:  1,
            19025:  1,
            19030:  2,
            19031:  0,
            19032:  0,
            19033:  0,
            19034:  0,
            19037:  1,
            19040:  1,
            19046:  1,
            19053:  1,
            19054:  1,
            19055:  1,
            19057:  0,
            19058:  0,
            19060:  2,
            19061:  1,
            19062:  5,
            19063:  2,
            19066:  0,
            19068:  1,
            19075:  1,
            19076:  1,
            19083:  1,
            19085:  1,
            19092:  1,
            19099:  0,
            19101:  1,
            19102:  1,
            19112:  1,
            19114:  0,
            19116:  2,
            19117:  2,
            19119: 23,
            19123:  1,
            19124:  1,
            19129:  2,
            19130:  2,
            19133:  2,
            19135:  0,
            19136:  1,
            19137:  1,
            19138:  1,
            19139:  2,
            19143:  0,
            19145:  1,
            19179:  2,
            20002:  2,
            20006:  2,
            20007:  2,
            20008:  2,
            20009:  2,
            20011:  2,
            20012:  0,
            20013:  2,
            20014:  2,
            20025:  2,
            20030:  3,
            20031:  0,
            20032:  0,
            20033:  0,
            20034:  0,
            20037:  2,
            20040:  2,
            20046:  2,
            20053:  2,
            20054:  2,
            20055:  2,
            20057:  0,
            20058:  0,
            20060:  2,
            20061:  2,
            20062:  2,
            20063:  2,
            20066:  0,
            20068:  2,
            20075:  2,
            20076:  2,
            20083:  2,
            20085:  2,
            20092:  2,
            20099:  0,
            20101:  2,
            20102:  2,
            20112:  2,
            20114:  0,
            20116:  2,
            20117:  2,
            20119:  2,
            20123:  2,
            20124:  2,
            20129:  3,
            20130:  3,
            20133:  3,
            20135:  0,
            20136:  2,
            20137:  2,
            20138:  2,
            20139:  2,
            20143:  2,
            20145:  2,
            20179:  3,
            21001:  4,
            27001:  0,
            28001:  0,
            29001:  0,
        }[self._value_]

    def IsCmd(self):
        """Returns True if this message is a request."""
        return (self._value_/1000) % 3 == 0

    def IsSuc(self):
        """Returns True if this message is a positive (ACK) response."""
        return (self._value_/1000) % 3 == 1

    def IsErr(self):
        """Returns True if this message is a negative (NAK) response."""
        return (self._value_/1000) % 3 == 2

if __name__ == "__main__":
    for name, member in ProtoNum.__members__.items():
        print "%-80r	%s" % (member, member.desc)

