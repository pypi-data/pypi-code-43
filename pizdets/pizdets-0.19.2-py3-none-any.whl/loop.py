pe.mix(1)
pe.close_valves()

#%%
def make_dilution(death_volume=0, peace_volume=10,extra_vacuum=5):
    pe.mix(1)
    pe.pump_death(t, death_volume)
    pe.pump_peace(t, peace_volume)
    pe.vacuum(t, death_volume+peace_volume)
    pe.mix(0)
    pe.vacuum(t, extra_vacuum)
    pe.mix(1)

while True:

    thresholds = read_thresholds_from_file() # 7 OD thresholds
    ODvalues = read_last_OD_values() # 7 OD values
    death_volumes = read_death_volumes() # 7 death volumes
    peace_volumes = 10 - death_volumes

    pe.mix(0)
    time.sleep(3)
    pe.record()
    pe.mix(1)

    for t in range(7):
        if ODvalues[t] < thresholds[t]:
            make_dilution(death_volume = death_volumes[t],
                          peace_volume = peace_volumes[t],
                          extra_vacuum=5)
        else:
            # wait a few seconds until the next measurement
            time.sleep(25)

