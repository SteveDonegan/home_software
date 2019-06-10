import shutil

__author__ = 'Steve'

import os, sys

from photograph import Photograph

from metadata import DIR_SUMMARY_FILENAME as DIR_SUMMARY_FILENAME, create_json_summary, update_json_summary

if __name__ == "__main__":

    dir_to_scan = sys.argv[1]
    archive_base_dir = sys.argv[2]

    if not os.path.exists(archive_base_dir):
        print "ERROR: %s does not exist!"
        sys.exit()

    cnt = 0
    dup_cnt = 0

    files_to_copy = []
    bad_files_found = []

    for root, dirs, files in os.walk(dir_to_scan):

        for filename in files:
            cnt += 1

            photo = None

            source_filename = os.path.join(root,filename)

            try:
                photo = Photograph(source_filename)

                #whats the new filename
                if photo:
                    photo.set_archived_filename()

                    photo.set_target_dirname(archive_base_dir)

                    target_file = os.path.join(photo.target_directory, photo.qualified_filename)

                    #todo: create method to check if file exists in qualified target dir - remember filename might not be
                    #exactly the same so do check based on md5
                    if os.path.exists((target_file)):

                        print "WARNING: Duplicate file in target dir: %s" %target_file

                        #if a file of that name already exists, check if md5 is the same
                        if photo.details['md5'] != photo.get_checksum(target_file):
                            raise Exception( "ERROR: Duplicate filename found but actual file contents different!")

                    elif not os.path.exists(target_file):

                        #create directory if needed
                        if not os.path.exists(photo.target_directory):
                            os.makedirs(photo.target_directory)

                        #copy file to new archive location
                        shutil.copy2(source_filename, target_file)

                        files_to_copy.append(target_file)

                    files_to_copy.append(target_file)

                    photo_json = photo.metadata_line()

                    #does target directory have a json summary file?
                    summary_filename = os.path.join(photo.target_directory,DIR_SUMMARY_FILENAME)

                    if not os.path.exists(summary_filename):

                        #create it
                        if create_json_summary(photo.target_directory):
                            print 'INFO: created base json summary file: %s' %summary_filename

                    else:
                        #add to it
                        if update_json_summary(summary_filename,photo_json):
                            print "worked"

                        else:
                            print "didnt work"


                    print "INFO: %s will be copied to %s" %(source_filename, target_file)

                    #update or create a new metadata file
                    #if not os.path.exists(os.path.join(photo.target_directory, photo.METADATA_FILENAME)):
                     #   print 'TODO: create function to create or update the metadata file'

                if filename not in files_to_copy:
                    files_to_copy.append(filename)

            except Exception as ex:
                print "ERROR: %s" %ex
                bad_files_found.append(filename)

#works first time around but then doesnt seem to be able to parse added to json next time round.

    print "Found %s files %s duplicated (%s bad files)!" %(cnt,dup_cnt, len(bad_files_found))
