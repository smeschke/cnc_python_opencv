import os
os.chdir('/home/stephen/Desktop')
sources = ['hawk72']#, 'cherryB']
for source in sources:
    #source = 'deer'

    with open('/home/stephen/Desktop/'+source+'.ngc') as f:
        read_data = f.read()
    print(len(read_data))
    read_data = read_data.replace("100.0", "#<z_speed>")
    read_data = read_data.replace("400.000000", "#<xy_speed>")
    print(len(read_data))
    file = open(source + "fixed.ngc", "a")
    file.write(read_data)
    file.close()
