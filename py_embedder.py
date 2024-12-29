#!/usr/bin/env python3

# --- INCLUDES ---
import argparse
import os
import re

# --- FUNCTION DECLARATION ---
'''
	get_file_size function
	@note : Wrapper for acquiring file size.
	@return : Return file size.
'''
def get_file_size( path ) :
	return os.stat( path ).st_size

'''
	load_source function
	@note : Load file and generate file information tuple.
	@param file_path : Query file path.
	@return : Return a tuple from file path, size and file content on 
			  source reading success.
'''
def load_source( file_path ):
	try :
		file = open( file_path, "rb" )

		file_size = get_file_size( file_path )
		file_data = file.read( )
	
		file.close( )

		return file_path, file_size, file_data
	except :
		print( f"> {file_path} can't be loaded." )

	return None

'''
	generate_file_path function
	@note : Generate embed file path from source path.
	@param file_path : Query source file path.
	@return : Return embed file path as source path with extension replaced 
			  with '_embed.h'.
'''
def generate_file_path( file_path ):
	split_path = file_path.split( '.' )
	split_id = 1
	path = split_path[ 0 ]

	while split_id < ( len( split_path ) - 1 ) :
		path += split_path[ split_id ]
		split_id += 1

	return path + "_embed.h"

'''
	get_name functon
	@note : Extract file name from file path.
	@param file_path : Query file path.
	@return : Return file name.
'''
def get_name( file_path ) :
	split_path = file_path.split( '/' )
	file_name = split_path[ len( split_path ) - 1 ]

	return file_name.split( '.' )[ 0 ].lower( )

'''
	get_guard function
	@note : Generate C include guard name from source file path.
	@param source_path : Query source file path.
	@return : Return C99 include guard name from source file path.
'''
def get_guard( source_path ) :
	guard = re.sub( "[\/\\.]", "_", source_path )
	
	return guard.upper( )

'''
	write_embed_guard method
	@note : Write embed file comments and header guard.
	@param file : Query embed file handle.
	@param source_path : Query source file path.
	@param guard : Query embed file guard name.
'''
def write_embed_guard( file, source_path, guard ) :
	file.write( f"/**\n * PY Embeder\n * Source : {source_path}\n **/\n" )
	file.write( f"#ifndef {guard}_H_\n#define {guard}_H_\n\n" )
	file.write( "#ifdef __cplusplus\nextern \"C\" {\n#endif\n\n" )

'''
	write_embed_header_file method
	@note : Write embed file byte array informations.
	@param file : Query embed file handle.
	@param source_size : Query source file size.
	@param name : Query embed file array name.
'''
def write_embed_header_file( file, source_size, name ) :
	file.write( f"const unsigned long g_embed_{name}_size = {source_size};\n" )
	file.write( f"const unsigned char g_embed_{name}_data[ {source_size} ] = {{\n\t" )

'''
	write_embed_header method
	@note : Write embed file C99 header.
	@param file : Query embed file handle.
	@param source_path : Query source file path.
	@param source_size : Query source file size.
'''
def write_embed_header( file, source_path, source_size ) :
	guard = get_guard( source_path )
	name = get_name( source_path )

	write_embed_guard( file, source_path, guard )
	write_embed_header_file( file, source_size, name )

'''
	write_embed_content method
	@note : Write source data as hex array.
	@param file : Query embed file handle.
	@param source_data : Query source data.
	@param is_final : True when it's last data buffer to write
'''
def write_embed_content( file, source_data, is_final ) :
	byte_id = 0	
	column = 0

	for byte in source_data :
		if ( byte_id == len( source_data ) - 1 ) and ( is_final == True ) :
			file.write( f"0x{byte:02X}" )
		else :
			file.write( f"0x{byte:02X}, " )

		byte_id += 1
		column += 1

		if column == 16 :
			column = 0

			file.write( "\n\t" )

'''
	write_embed_footer method
	@note : Write embed C99 footer.
	@param file : Query embed file handle.
	@param source_path : Query source file path.
'''
def write_embed_footer( file, source_path ) :
	guard = get_guard( source_path )

	file.write( "\n};\n\n" )
	file.write( "#ifdef __cplusplus\n};\n#endif\n\n" )
	file.write( f"#endif /* !{guard}_H_ */\n" )

'''
	write_embed method
	@note : Write an embed file.
	@param file_path : Query embed file path.
	@param file_info : Query source file information tuple.
'''
def write_embed( file_path, file_info ):
	try :
		embed_file = open( file_path, "w" )

		write_embed_header( embed_file, file_info[ 0 ], file_info[ 1 ] )
		write_embed_content( embed_file, file_info[ 2 ], True )
		write_embed_footer( embed_file, file_info[ 0 ] )

		embed_file.close( )

		print( f"> Generated file :'{file_path}'" )
	except :
		print( "> Failure during file writing." )

'''
	generate_embed_file method
	@note : Generate embed file from a source file.
	@param file_path : Query source file path.
'''
def generate_embed_file( file_path ) :
	if not os.path.isfile( file_path ) :
		print( "> Specified source path is not a file." )

		return

	if ( len( file_path ) == 0 ) :
		print( "> Source file path can't be empty for generating a C embed wrapper." )
		
		return

	file_info = load_source( file_path )
	file_path = generate_file_path( file_path )

	if file_info is None :
		print( "> Source file information can't be acquired by 'load_source' call." )

		return
	
	write_embed( file_path, file_info )

'''
	generate_embed_directory method
	@note : Generate embed file for all files store in query directory.
	@param directory_path : Query directory path.
'''
def generate_embed_directory( directory_path ):
	if not os.path.isdir( directory_path ) :
		print( f"> Specified path : {directory_path} is not a directory." )

		return

	for file in os.scandir( directory_path ):
		if file.is_file( ) :
			print( f"> {file.path}" )

			generate_embed_file( file.path )

'''
	generate_combine_list function
	@note : Generate file list.
	@param directory_path : Query directory path.
	@param embed_path : Query embed file path.
	@return : Return list of tuple composed by file name and size.
'''
def generate_combine_list( directory_path, embed_path ) :
	file_list = [ ]
	length = 0
	count = 0

	for file in os.scandir( directory_path ):
		if file.is_file( ) and not ( file.path == embed_path ) :
			file_name = file.name.split( '.' )[ 0 ]
			file_name = re.sub( "[\/\\.-]", "_", file_name )
			file_size = get_file_size( file.path )

			file_list.append( ( file_name, length ) )
			
			length += file_size
			count += 1

	return length, count, file_list

'''
	generate_embed_combine method
	@note : Generate one embed file for all files store in query directory.
'''
def generate_embed_combine( directory_path ):
	if not os.path.isdir( directory_path ) :
		print( f"> Specified path : {directory_path} is not a directory." )

		return

	split_path = re.split( '[//\/]', directory_path )
	
	name = split_path[ len( split_path ) - 2 ]
	embed_path = directory_path + name + "_embed.h"
	file_path = directory_path + name + ".h"
	length, count, file_list = generate_combine_list( directory_path, embed_path )

	try :
		embed_file = open( embed_path, "w" )
		
		# write basic header
		write_embed_guard( embed_file, file_path, name.upper( ) )

		embed_file.write( "// --- OFFSETS ---\n" )
		
		# Generate offsets list
		for element in file_list :
			embed_file.write( f"const unsigned long g_embed_{element[ 0 ]}_offset = {element[ 1 ]};\n" )
		
		# write blob data
		embed_file.write( "\n// --- DATA BLOB ---\n" )

		write_embed_header_file( embed_file, length, name )

		for file in os.scandir( directory_path ):
			if file.is_file( ) and not ( file.path == embed_path ) :
				print( f"> {file.path}" )
				
				count -= 1
				file_info = load_source( file.path )

				write_embed_content( embed_file, file_info[ 2 ], ( count == 0 ) )

				if ( count > 0 ) :
					embed_file.write( "\n\t" )
		
		# write basic footer
		write_embed_footer( embed_file, file_path )

		embed_file.close( )

		print( f"> Generated file :'{embed_path}'" )
	except :
		print( "> Failure during file writing." )

'''
	has_path_argument function
	@note : Basic multiple argument check.
	@param arguments : Current argument list.
	@return : Return True when arguments contain at leat two elements.
'''
def has_path_argument( arguments ):
	length = len( arguments )

	if ( length < 2 ) :
		print( f"> Command '{arguments[ 0 ]}' need at least one argument." )

	return length > 1

# --- MAIN LOOP ---
if __name__ == '__main__':
	print( "=== PY Embeder ===" )
	print( "> Utility tool for generating C99 header for embedded files.\n" )

	parser = argparse.ArgumentParser( )

	parser.add_argument( '-f', '--file', type=str, nargs='*', help='Generate embed file for a file or file list.' )
	parser.add_argument( '-d', '--directory', type=str, nargs='*', help='Generate embed file for all files of a directory.' )
	parser.add_argument( '-c', '--combine', type=str, nargs='*', help='Generate one embed file who contain all files of a directory.' )

	arguments = parser.parse_args( )

	if arguments.directory is not None :
		for directory_path in arguments.directory :
			generate_embed_directory( directory_path )
	elif arguments.combine is not None :
		for directory_path in arguments.combine :
			generate_embed_combine( directory_path )
	elif arguments.file is not None :
		for file_path in arguments.file :
			generate_embed_file( file_path )
