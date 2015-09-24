from rpi_commu_package import commu

rpi_commu = commu()

commu.run_threads()

while True:
    for x in range(16):
        print "id ", x, ": ",  commu.get_data(x)
