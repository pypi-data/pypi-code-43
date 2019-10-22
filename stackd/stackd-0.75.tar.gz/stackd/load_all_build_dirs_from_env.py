def load_all_build_dirs_from_env(env_vars={}, build_dirs=[]):
  env_var_prefix = 'STACKD_BUILD_DIR_'
  env_var_prefix_len = len(env_var_prefix)
  for key, val in env_vars.items() :
    if key[:env_var_prefix_len] == env_var_prefix and val != '' and val not in build_dirs:
      build_dirs.append(val)
  return build_dirs