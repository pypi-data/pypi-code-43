#! /usr/bin/python
# -*- coding: utf-8 -*-
from urllib.parse import urlparse
from six.moves import http_client
import xlrd
import Augmentor
import mimetypes
from foqus.commons import resize_images, download

from foqus.mqueue import *
from foqus.customers import *
from foqus.request_api import *
from urllib.request import urlopen
import tensorflow as tf

api = APIFoqus()

def load_labels(label_file):
    if '://' in label_file:
        response = urlopen(label_file)
        proto_as_ascii_lines = response.read()
        label = proto_as_ascii_lines.decode('utf-8').split('\n')
    else:
        label = []
        proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
        for l in proto_as_ascii_lines:
            label.append(l.rstrip())
    return label


def count_images_folders(path):
    x = 0
    for i in os.listdir(str(path)):
        x = x + 1
    return x


def load_graph(model_file):
    if '//' in model_file:
        try:

            logger.info('Getting graph from %s' %model_file)
            response = urlopen(model_file).getcode()
            if response == 200:
                graph = tf.Graph()
                graph_def = tf.GraphDef()
                file = urlopen(model_file)
                file_content = file.read()
                graph_def.ParseFromString(file_content)
                with graph.as_default():
                    tf.import_graph_def(graph_def)
                return graph
            else:
                logger.info('file %s Not exisiting in server' %model_file)

        except Exception as e:
            logger.error('Error %s in getting graph from remote server %s'% (e, model_file))
    else:
        graph = tf.Graph()
        graph_def = tf.GraphDef()

        with open(model_file, "rb") as f:
            graph_def.ParseFromString(f.read())
        with graph.as_default():
            tf.import_graph_def(graph_def)
        return graph
    return None


def load_json_data(json_path):
    try:
        with open(json_path) as data_file:
            json_input = json.load(data_file)
    except:
        json_data = open(json_path)
        bom_maybe = json_data.read(3)
        if bom_maybe != codecs.BOM_UTF8:
            json_data.seek(0)
        json_input = json.load(json_data)
    return json_input


def checkUrl(url):
    p = urlparse(url)
    conn = http_client.HTTPConnection(p.netloc)
    conn.request('HEAD', p.path)
    resp = conn.getresponse()
    return resp.status < 400


def is_url_image(image_url):
   image_formats = ("image/png", "image/jpeg", "image/jpg")
   r = requests.head(image_url)
   if r.headers["content-type"] not in image_formats:
       mimetype, encoding = mimetypes.guess_type(image_url)
       return (mimetype and mimetype.startswith('image'))
   else:
       return True


def image_extension(image_url):
    r = requests.head(image_url)
    return (r.headers["content-type"].split('/')[1])


def verif_folder_less_twenty(path):
    image_ext = ['.jpg' , '.png' , '.JPG', '.PNG']
    folder_less_20 = []
    max_nb = 20
    for j in os.listdir(path):

        x = 0
        for i in os.listdir(str(path) + "/" + str(j)):
            if os.path.splitext(i)[1] in image_ext:
                x = x + 1
        if (x <= 20 or x < max_nb):
            logger.warning("WARNING: Folder has less images : " + str(j).split('/')[-1])
            folder_less_20.append(str(j).split('/')[-1])
        else :
            if x > max_nb:
                max_nb = x
    return folder_less_20, max_nb


def generate_more_images(training_path, folders, max_nb):
    for id_categorie in folders:
        DIR = str(training_path) + "/" + str(id_categorie)
        nb_images = (len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))]))
        p = Augmentor.Pipeline(source_directory=DIR, output_directory=DIR)
        p.rotate(probability=1, max_left_rotation=5, max_right_rotation=5)
        p.flip_left_right(probability=0.5)
        p.zoom_random(probability=0.5, percentage_area=0.8)
        p.flip_top_bottom(probability=0.5)
        p.sample(max_nb - nb_images)
    logger.info("The images increase is done successfully")


def read_tensor_from_image_file(file_name, input_height=299, input_width=299, input_mean=0, input_std=255):
    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.read_file(file_name, input_name)
    if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(file_reader, channels = 3,
                                           name='png_reader')
    elif file_name.endswith(".gif"):
        image_reader = tf.squeeze(tf.image.decode_gif(file_reader,
                                                      name='gif_reader'))
    elif file_name.endswith(".bmp"):
        image_reader = tf.image.decode_bmp(file_reader, name='bmp_reader')
    else:
        image_reader = tf.image.decode_jpeg(file_reader, channels = 3,
                                            name='jpeg_reader')
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0);
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.Session()
    result = sess.run(normalized)
    return result


def fill_prediction_table(path_file_Final,customer_type, customer_name, customer_universe):
    table_name = "predict_" + customer_type + '_' + customer_name + '_' + customer_universe
    db.create_prediction_table(table_name)
    workbook = xlrd.open_workbook(path_file_Final)
    sheet = workbook.sheet_by_name(workbook.sheet_names()[0])
    nRows = sheet.nrows

    db.delete_predict_table(table_name)
    for i in range(1, nRows):
        row_values = sheet.row_values(i)
        if row_values[12] != "":
            principal_categorie = str((row_values[12]))
        else:
            if row_values[10] != "":
                principal_categorie = str((row_values[10]))
            else:
                principal_categorie = str((row_values[8]))
        db.add_prediction_table(table_name, row_values, principal_categorie)


def process_customer_stream_from_json(json_path, customer_name, customer_type, project_name):
    request_post = api.apipost('retrieve_images_json', customer_name, customer_type, project_name,json_path)
    response_text = json.loads(request_post.text)
    response = response_text['response']
    if int(response) != 0:
        generate_similarity_vector(customer_name, customer_type, project_name)


def process_customer_stream_cms(json_path, customer_name, customer_type, project_name):
    streams_path = STREAMS_PATH + customer_type + '/' + customer_name + '/similars/' + project_name + '/'+ \
                   'cms_json_file.json'
    streams_paths3 = STREAMS_S3 + customer_type + '/' + customer_name + '/similars/' + project_name + '/'
    if '://' in json_path:
        download(json_path, streams_path)
    else:
        streams_path = json_path
    upload_file_into_s3(streams_path, streams_paths3)
    # TODO appel fonction process customer from stream après traitement de fichier json des produits
    # process_customer_stream_from_json(json_path, customer_name, customer_type,project_name)


def detection_error_training(excel_path, customer_name, customer_type, customer_universe):
    api.apipost('training_text_detection', customer_name, customer_type, None, excel_path, customer_universe)


def equilibrate_customer_samples_count(excel_path, customer_name, customer_type, customer_universe):
    api.apipost('correction_training', customer_name, customer_type, None, excel_path, customer_universe)


def shopify_training(customer_name, customer_type, url_shop, project, INPUT_SESSION_UUID):
    api.apipost('shopify_training', customer_name, customer_type, None, None, project, url_shop, INPUT_SESSION_UUID)


def generate_similarity_vector(customer_name="vector", customer_type='vector', project_name=None):
    api.apipost('training_similars', customer_name, customer_type, project_name, None, None)

