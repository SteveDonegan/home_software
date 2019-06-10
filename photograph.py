import json

__author__ = 'Steve'

import hashlib
from datetime import datetime
from PIL import Image

from PIL.ExifTags import TAGS

import os

class Photograph(object):
    '''
        Class to characterise a single photo and provide methods on this

    '''

    FORMATS = ['.jpg','.jpeg','.JPEG','.JPG']

    METADATA_FILENAME = 'photo_summary.txt'

    def metadata_line(self):
        '''
            Method to return a line summarising photograph for inclusion in database or similar
        '''

        #format for a csv line
        #original_filename, archived_filename, original_date, targetdir, format, md5, archive date, camera

        arc_dt = datetime.now().strftime("%Y%m%d%H%M")

        pic_details = {'filename':self.filename, 'qualified_file':self.qualified_filename, 'img_date':self.details['datestring'],
                        'target_directory':self.target_directory,'extension':self.details['extension'],'md5':self.details['md5'],
                        'archive_date':arc_dt,'camera':self.details['camera']}

        #comma_del_line='%s,%s,%s,%s,%s,%s,%s' %(self.filename, self.qualified_filename, self.details['datestring'],self.target_directory,
                                        #self.details['extension'], self.details['md5'], arc_dt, self.details['camera'])

        return json.dumps(pic_details)



    def set_archived_filename(self):
        '''
            Method to return the archive filename in format:

            YYYYMMDDTHHMMSS_YYYYMMDDTHHMMSS_YYYYMMDDTHHMMSS_NNNNNNNNNN_CCCCCCC.ext

            where each block separeted by "-":
            block1: original_acquisition date-time
            block2: Original camera filename padded to 10 chars with "_" char
            block3: Original camera model name padded t0 10 chars with "_" char
        '''

        qualified_filename = None

        block1 = '%s%s%s%s%s%s' %(self.details['year'] ,self.details['month'],self.details['day'], \
                                    self.details['hour'], self.details['minute'], self.details['second'])

        #todo: grab this from previous filename
        #block2 = datetime.now().strftime("%Y%m%d%H%M")

        #block3 = datetime.now().strftime("%Y%m%d%H%M")

        block2 = os.path.splitext(os.path.basename(self.filename))[0].zfill(12)

        block3 = self.details['camera'].zfill(12)

        ext = self.details['extension']

        self.qualified_filename = '%s_%s_%s%s' %(block1,block2,block3,ext)


    def set_target_dirname(self, base_directory):
        '''
        Method to set the target directory

        '''

        self.target_directory = os.path.join(base_directory, self.details['year'], self.details['month'], self.details['day'])


    def get_exif_header(self,filename):
        '''
            Method to return a dictionary of EXIF headers

        :param filename: filename of image
        :return: dictionary of exif headers
        '''

        try:
            ret = {}
            i = Image.open(filename)
            info = i._getexif()
            for tag, value in info.items():
                decoded = TAGS.get(tag, tag)
                ret[decoded] = value

        except Exception as ex:
            ret = None

        return ret

    def get_checksum(self,data_file):
        '''
        Method to check the actual checksum of the data against the value in the checksum file TBC
        :return:
        '''

        md5 = hashlib.md5()

        try:
            datafile = open(data_file)

            for line in datafile:
                md5.update(line)

            datafile.close()

            return md5.hexdigest()

        except Exception as ex:
            raise Exception ("Could not calculate checksum for: %s (%s)" %(data_file,ex))


    def get_image_details(self,header):
        '''
            Method to extract basic image details

        :param filename:
        :return:
        '''
        details = {}

        #get useful info
        try:
            details['img_date_str'] = header['DateTime']
            details['camera'] = header['Model']

        except Exception as ex:
            raise Exception("Could not extract info from header dict (%s)" %ex)

        #get specific year month day info
        details['year'] = None
        details['month'] = None
        details['day'] = None
        details['hour'] = None
        details['minute'] = None
        details['second'] = None

        details['extension'] = None

        #file size
        details['size'] = None

        try:
            #TODO: is this consistent for all cameras i.e. following standard EXIF header
            details['year'] = header['DateTime'].split(' ')[0].split(':')[0]
            details['month'] = header['DateTime'].split(' ')[0].split(':')[1]
            details['day'] = header['DateTime'].split(' ')[0].split(':')[2]

            details['hour'] = header['DateTime'].split(' ')[1].split(':')[0]
            details['minute'] = header['DateTime'].split(' ')[1].split(':')[1]
            details['second'] = header['DateTime'].split(' ')[1].split(':')[2]

            details['datestring'] = '%s%s%s%s%s%s' %(details['year'], details['month'], details['day'],
                                                     details['hour'], details['minute'], details['second'])

            details['extension'] = os.path.splitext(self.filename)[-1].lower()

        except Exception as ex:
            raise Exception("Could not extract date info from header dict (%s)" %ex)

        #information on the file itself
        try:
            details['size'] = os.path.getsize(self.filename)

        except Exception as ex:
            raise Exception("Could not extract file system size (%s)" %ex)

        #information on the file md5
        try:
            details['md5'] = self.get_checksum(self.filename)

        except Exception as ex:
            raise Exception("Could not extract file system size (%s)" %ex)

        return details


    def __init__(self, filename):

        self.filename = filename

        #is file an image or move file
        if  os.path.splitext(os.path.basename(filename))[1] not in self.FORMATS:
            raise Exception ('Not a valid image format')

        #get headers
        try:
            header = self.get_exif_header(filename)

            if not header:
                raise Exception ("Could not access EXIF headers")

        except Exception as ex:
            raise Exception("Error could not access header: %s" %ex)

        try:
            self.md5 = self.get_checksum(filename)

        except Exception as ex:
            raise Exception ("Cannot calulate checksum %s" %ex)

        try:
            self.details = self.get_image_details(header)

        except Exception as ex:
            raise Exception ("Cannot extract and assign photograph detailed information")

