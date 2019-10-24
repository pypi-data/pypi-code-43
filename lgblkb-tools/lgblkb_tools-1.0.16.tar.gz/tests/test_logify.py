from lgblkb_tools import logger,Folder

# logs_path=Folder('logs')['logs.log']

# logger.add_file_handler(log_folder['logs.log'])
# logger=TheLogger('lgblkb_tools').to_stream().to_rotate(logs_path)

@logger.trace()
def do_something():
	pass

@logger.trace()
def main():
	this_folder=Folder(__file__)
	for child in this_folder.children:
		logger.info('child: %s',child)
	do_something()

	pass

if __name__=='__main__':
	main()
