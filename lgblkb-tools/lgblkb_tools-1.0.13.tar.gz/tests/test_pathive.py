import pytest

from lgblkb_tools.pathify import *

this_folder_name=os.path.split(os.path.dirname(__file__))[-1]
this_file_name=os.path.split(os.path.splitext(__file__)[0])[-1]

@pytest.fixture()
def this_filepath():
	return __file__

@pytest.fixture()
def this_folder():
	return Folder()

@pytest.fixture()
def some_dirpath():
	return os.path.split(__file__)[0]

def test_get_name(this_filepath):
	name=get_name(this_filepath)
	assert name==this_file_name

def test_get_parent_dir(this_filepath):
	parent_dir=get_parent_dir(this_filepath)
	assert parent_dir==os.path.split(this_filepath)[0]

def test_create_path(this_filepath,some_dirpath):
	created_path=create_path(this_filepath,stop_depth=1)
	assert os.path.exists(created_path)
	assert created_path==this_filepath

	created_path=create_path(some_dirpath,stop_depth=0)
	assert os.path.exists(created_path)
	assert created_path==some_dirpath

def test_get_splitted(this_filepath):
	parts=get_splitted(this_filepath)
	assert parts[-1]==this_file_name+'.py'
	assert parts[-2]==this_folder_name

def test_create_zipfile(some_dirpath):
	zipfile_path=create_zipfile(some_dirpath)
	assert get_name(zipfile_path)==this_folder_name
	os.remove(zipfile_path)

def test_folder(this_folder: Folder,this_filepath):
	name_args=[1,2,'some_param']
	assert get_name(this_folder.get_filepath(*name_args,delim='__'))=='1__2__some_param'
	assert this_folder.get_filepath(*name_args,ext='.qwe').endswith('1_2_some_param.qwe')
	assert get_name(this_folder.get_filepath(datetime_loc_index=0)).split('_')[0]==str(datetime.today().date())
	assert this_folder.exists
	assert this_filepath in Folder(__file__).glob_search('*')

	tmp_folder=this_folder.create('tmp').clear()
	assert tmp_folder.exists
	assert tmp_folder.create('subdir1').parent().name=='tmp'

	tmp2_folder=this_folder.create('tmp2').clear()
	tmp2_folder['qwe.txt']=123
	copied_folder=tmp2_folder.copy_to(tmp_folder)
	assert copied_folder.name==tmp2_folder.name
	assert copied_folder.parent()==tmp_folder
	assert get_name(copied_folder.children[0])=='qwe'

	assert tmp2_folder.exists
	tmp2_folder.delete()
	assert not tmp2_folder.exists

	src_folder=tmp_folder['tmp_test_src_folder']
	copied_folder.move_to(src_folder)
	assert copied_folder.parent()==src_folder

	for i in range(10):
		iter_folder=copied_folder.create('some_folder',iterated=True)
		assert iter_folder.name=='some_folder_'+str(i)

	zip_filepath=src_folder.zip()
	assert get_name(zip_filepath)==src_folder.name

	safe_folder=tmp_folder.create('qfnowdaofnwoawd.SAFE')
	assert safe_folder.name.endswith('.SAFE')
	for i in range(10):
		safe_folder[f'some_file_{i}.json']=dict(i=1,some_text='fqowaufboadowaodbaw')
	assert len(safe_folder.children)==10
	zip_filepath=safe_folder.zip()
	assert zip_filepath.endswith('.SAFE.zip')

	zip_filepath=safe_folder.zip(safe_folder.name.replace('.SAFE',''))
	assert Folder(zip_filepath)==safe_folder.parent()
	assert not zip_filepath.endswith('.SAFE.zip')

	src_folder.unzip(zip_filepath,create_subdir=False)
	# assert zip_filepath.rstrip('.zip')==''
	new_safe_folder=src_folder.create(zip_filepath.replace('.zip','.SAFE'),reactive=False)
	assert new_safe_folder.exists
	assert new_safe_folder.name==safe_folder.name
	tmp_folder.delete()
	assert not tmp_folder.exists
