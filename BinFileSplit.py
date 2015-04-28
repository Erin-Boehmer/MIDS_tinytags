infile = open('/Users/Kazuki/Desktop/tiny_images.bin', 'rb')
byte_count = 32 * 32 * 3

image_count = 79302017
for i in range(0, 80):
	outfile_name = "/Volumes/My Book 3.0/images/%sm_%sm.bin" % (str(i), str(i + 1))
	outfile = open(outfile_name, 'wb')
	for j in range(i*1000000, min((i+1)*1000000, image_count)):
		data = infile.read(byte_count)
		outfile.write(data)
	outfile.close()
	print("wrote out %s" % outfile_name)
