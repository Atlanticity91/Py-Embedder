import os
import re

# --- FUNCTION DECLARATION
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
		print( "> {0} can't be loaded.".format( file_path ) )

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
	write_embed_header method
	@note : Write embed file C99 header.
	@param file : Query embed file handle.
	@param source_path : Query source file path.
	@param source_size : Query source file size.
'''
def write_embed_header( file, source_path, source_size ) :
	guard = get_guard( source_path )
	name = get_name( source_path )

	file.write( "/**\n * PY Embeder\n * Source : {0}\n **/\n".format( source_path ) )
	file.write( "#ifndef {0}_H_\n#define {0}_H_\n\n".format( guard ) )
	file.write( "#ifdef __cplusplus\nextern \"C\" {\n#endif\n\n" )
	file.write( "const unsigned long g_embed_{0}_size = {1};\n".format( name, source_size ) )
	file.write( "const unsigned char g_embed_{0}_data[ {1} ] = {{\n\t".format( name, source_size  ) )

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
			file.write( "0x{:02X}".format( byte ) )
		else :
			file.write( "0x{:02X}, ".format( byte ) )

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
	file.write( "#endif /* !{0}_H_ */\n".format( guard ) )

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

		print( "> Generated file :'{0}'".format( file_path ) )
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
		print( "> Specified path : {0} is not a directory.".format( directory_path ) )

		return

	for file in os.scandir( directory_path ):
		if file.is_file( ) :
			print( "> {0}".format( file.path ) )

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
		print( "> Specified path : {0} is not a directory.".format( directory_path ) )

		return

	split_path = re.split( '[//\/]', directory_path )
	
	name = split_path[ len( split_path ) - 2 ]
	embed_path = directory_path + name + "_embed.h"
	file_path = directory_path + name + ".h"
	length, count, file_list = generate_combine_list( directory_path, embed_path )

	try :
		embed_file = open( embed_path, "w" )
		
		# write basic header
		embed_file.write( "/**\n * PY Embeder\n * Source : {0}\n **/\n".format( file_path ) )
		embed_file.write( "#ifndef {0}_H_\n#define {0}_H_\n\n".format( name.upper( ) ) )
		embed_file.write( "#ifdef __cplusplus\nextern \"C\" {\n#endif\n\n" )
		embed_file.write( "// --- OFFSETS ---\n" )
		
		# Generate offsets list
		for element in file_list :
			embed_file.write( "const unsigned long g_embed_{0}_offset = {1};\n".format( element[ 0 ], element[ 1 ] ) )
		
		# write blob data
		embed_file.write( "\n// --- DATA BLOB ---\n" )
		embed_file.write( "const unsigned long g_embed_{0}_size = {1};\n".format( name, length ) )
		embed_file.write( "const unsigned char g_embed_{0}_data[ {1} ] = {{\n\t".format( name, length  ) )

		for file in os.scandir( directory_path ):
			if file.is_file( ) and not ( file.path == embed_path ) :
				print( "> {0}".format( file.path ) )
				
				count -= 1
				file_info = load_source( file.path )

				write_embed_content( embed_file, file_info[ 2 ], ( count == 0 ) )

				if ( count > 0 ) :
					embed_file.write( "\n\t" )
		
		# write basic footer
		write_embed_footer( embed_file, file_path )

		embed_file.close( )

		print( "> Generated file :'{0}'".format( embed_path ) )
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
		print( "> Command '{0}' need at least one argument.".format( arguments[ 0 ] ) )

	return length > 1

'''
	print_command method
	@note : Wrapper for command print.
	@param command : Query command name.
	@param format : Query command usage formated.
'''
def print_command( command, format ):
	print( "> Use '{0}{1}".format( command, format ) )

# --- COMMAND LIST ---
CMD_QUIT = "-q"
CMD_DIRECTORY = "-d"
CMD_COMBINE = "-c"

# --- PRETTY HEADER ---
print( "=== PY Embeder ===" )
print( "> For single file ")
print_command( CMD_QUIT, "' for quiting." )
print_command( CMD_DIRECTORY, " path' for generating embed file for a directory." )
print_command( CMD_COMBINE, " path' for generating one embed file for a directory." )
print( "" )

# --- MAIN LOOP ---
while True :
	arguments = input( "> " ).split( ' ' )

	if arguments[ 0 ] == CMD_QUIT :
		print( "> Bye" )

		break
	elif arguments[ 0 ] == CMD_DIRECTORY :
		if has_path_argument( arguments ) :
			for argument_id in range( 1, len( arguments ) ):
				generate_embed_directory( arguments[ argument_id ] )
	elif arguments[ 0 ] == CMD_COMBINE :
		if has_path_argument( arguments ) :
			for argument_id in range( 1, len( arguments ) ):
				generate_embed_combine( arguments[ argument_id ] )
	else :
		for file_path in arguments :
			generate_embed_file( file_path )
