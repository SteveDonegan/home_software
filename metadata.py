import json
import os

__author__ = 'Steve'

from datetime import datetime

#every directory created with photos in shall have a summary json file.  This is its name
DIR_SUMMARY_FILENAME = 'directory_summary.json'

def create_json_summary(directory):
    '''
    Method to create a jason summary file
    :return:
    '''

    if not os.path.exists(directory):
        raise Exception("target directory does not exist")

    create_dt  = datetime.now().strftime("%Y%m%d%H%M")

    #get the bare bones
    json_summary = create_json_top_level(directory, create_dt)

    summary_file = os.path.join(directory,DIR_SUMMARY_FILENAME)

    #generate the file
    with open(summary_file, 'w') as fp:
        json.dump(json_summary, fp)

    if os.path.exists(summary_file):
        return True

    else:
        return False


def update_json_summary(filename, metadata_line):
    '''
    Method to update an existing metadata file
    :param filename:
    :return:
    '''

    updated = False

    #open existing json file
    if not os.path.exists(filename):
        raise Exception ("JSON file %s does not exist!" %(filename))

    try:
        #with open(filename) as json_data:
         #   json_metadata = json.load(json_data)
        json_metadata = read_json(filename)

    except Exception as ex:
        raise Exception ("Unable to open or parse JSON file: %s" %(filename))

    #add to it
    #https://stackoverflow.com/questions/18980039/how-to-append-in-a-json-file-in-python

    try:
        json_metadata[metadata_line['qualified_file']] = metadata_line

        if dump_to_json_file(filename,json_metadata):
            updated = True

    except Exception as ex:
        raise Exception ("Unable to add content to JSON file: %s" %(filename))

    return updated



def create_json_top_level(directory, create_date):
    '''
    Method to return the top level json wrapper to which we later add the individual photo json bits
    :return:
    '''

    #create an initial dict object to serialise
    dir_dict = {'directory':directory, 'create_date':create_date, 'update_date':None}

    return json.dumps(dir_dict)

#from ceda json demo
def dump_to_json_file(filename, dict_content):
    '''
    Method to dump a dict content to json.  Will remove any previous file of that name and create new
    :return: Boolean
    '''

    # open a file list and write the output list to it.
    if os.path.exists(filename):
        os.remove(filename)

    # convert to json object first
    '''

    '''
    # write to file
    try:
        with open(filename, 'w') as jsonob:
            json.dump(dict_content, jsonob)

    except Exception as ex:
        raise Exception("Cannot dump json to file! (%s)" % ex)

    if os.path.exists(filename):
        return True

    else:
        return False


def read_json(filename):
    '''
    Method to read content from json file and return as dict object
    :param filename: json object saved previously.  Must be structure used in pre-process extract
    :return: content rendered as python object
    '''
#with open(filename) as json_data:
         #   json_metadata = json.load(json_data)
    try:
        #with open(filename, 'r') as jsonob:
            #extracted = json.loads(byteify(json.loads(jsonob)))
         #   extracted = byteify(json.loads(json.load(jsonob)))
        with open(filename) as json_data:
            extracted = json.load(json_data)

        return extracted

    except Exception as ex:
        raise Exception("Cannot read json from file! (%s)" % ex)


def byteify(input):
    '''
    Method to convert output from  JSON  stored object
    #from http://stackoverflow.com/questions/956867/how-to-get-string-objects-instead-of-unicode-ones-from-json-in-python
    :param input:
    :return:
    '''
    if isinstance(input, dict):
        return {byteify(key): byteify(value)
                for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [byteify(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('utf-8')
    else:
        return input

