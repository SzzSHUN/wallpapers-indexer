#!/bin/env python
# vim: ts=4:sw=4:sts=4:noet:ai
# Készítette a PingvinSarok közösség számára:
# SzzS (info [kukac] szarkazsolt [pont] hu)

import sys
import os
import getopt
from PIL import Image, ExifTags

SCRIPTNEV="wallpapers-indexer.py"
SCRIPTVERZIO="20210408.2051"
#Globális változók értékének feltöltése az lapértelmezésekkel
WALLPAPERS_DIR="."
KIMENETFAJLNEV="INDEX.md"
OUTPUT_MD=f"{WALLPAPERS_DIR}/{KIMENETFAJLNEV}"
IMAGE_WIDTH=150

#Üzenet kiírása a standard hibakimenetre
def print_to_stderr(*szoveg):
	print(*szoveg, file = sys.stderr)

#Byte összeg átalakítás olvashatóbb formátumba
def kilo_mega_giga(int_byte):
	sResult=f"{int_byte} Byte"
	if( float(int_byte)/float(2**30) > 1.0 ):
		sResult="{:.2f} GB".format(float(int_byte)/float(2**30))
	elif( float(int_byte)/float(2**20) > 1.0 ):
		sResult="{:.2f} MB".format(float(int_byte)/float(2**20))
	elif( float(int_byte)/float(2**10) > 1.0 ):
		sResult="{:.2f} KB".format(float(int_byte)/float(2**10))
	return sResult

#Parancssori paraméterek feldolgozása
# True értékkel tér vissza, ha megkezdhető a munka.
def ParancssorFeldolgozasa():
	global OUTPUT_MD, WALLPAPERS_DIR, KIMENETFAJLNEV, IMAGE_WIDTH
	bResult = True
	SCRIPTNEV = sys.argv[0]
	if( len(sys.argv) > 1 ):
		try:
			opts, args = getopt.getopt(sys.argv[1:],None,["help","version","kepek=","kimenet=","kepszelesseg="])
		except getopt.GetoptError as e:
			bResult = False
			print(e)
			ParancssorSugo()
			return bResult
		for opt, arg in opts:
			if( opt == "--help"):
				bResult = False
				ParancssorSugo()
			elif( opt == "--version" ):
				bResult = False
				ParancssorVerzio()
			elif( opt == "--kepek" ):
				WALLPAPERS_DIR = arg
			elif( opt == "--kimenet" ):
				KIMENETFAJLNEV = arg
			elif( opt == "--kepszelesseg" ):
				IMAGE_WIDTH = arg
	OUTPUT_MD=f"{WALLPAPERS_DIR}/{KIMENETFAJLNEV}"
	return bResult

#Súgó szöveg kiírása
def ParancssorSugo():
	global SCRIPTNEV,SCRIPTVERZIO,IMAGE_WIDTH
	print(f"""Név: {SCRIPTNEV}
Verzió: {SCRIPTVERZIO}
Leírás: PingvinSarok közösség Wallpapers repójának indexelője
Használat:{SCRIPTNEV} [PARAMÉTEREK]

Paraméterek:
	--kepek
		Háttérképfájlokat tartalmazó könyvtár útvonalának megadása.
		Ha nincs megadva, akkor az aktuális köyvtár lesz beállítva ( ./ )

	--kimenet
		A kimeneti fájl neve
		Ha nincs megadva, akkor INDEX.md

	--kepszelesseg
		A táblázatban megjelenő index kép szélessége pixelben.
		Az alapértelmezett érték: {IMAGE_WIDTH} 

	--help
		Megjeleníti a  súgó szövegét és kilép

	--version
		Kiírja a program verzióját és kilép.

Példák:
		{SCRIPTNEV} --help
		
		{SCRIPTNEV} --kepek=~/GITHUB/Könyvtárnév\ szóközzel

		{SCRIPTNEV} --kepek=~/GITHUB/Hatter --kimenet=README.md --kepszelesseg=320
	""")

#A script verziójának kiírása
def ParancssorVerzio():
	global SCRIPTVERZIO
	print(SCRIPTVERZIO)

#Képek feldolgozása
def KepekFeldolgozasa():
	global OUTPUT_MD, WALLPAPERS_DIR, KIMENETFAJLNEV, IMAGE_WIDTH
	print(f"Képfájlok könyvtára: {WALLPAPERS_DIR}")
	print(f"Kimeneti fájl: {OUTPUT_MD}")
	print(f"Képek szélessége: {IMAGE_WIDTH}px")

	#Ellenőrizzük a WALLPAPERS_DIR globális változóban megadott könyvtár meglétét.
	if( os.path.isdir(WALLPAPERS_DIR) == True ):
		#Ha a könyvtár létezik, akkor végigjárjuk a könyvtár képeit és kiírjuk az adatokat az OUTPUT_MD változó által meghatározott fájlba.
		FilePointer = None
		kepfajlok = []
		try:
			print("Képek feldolgozása...")
			for dirfile in os.scandir(path=WALLPAPERS_DIR):
				if( dirfile.path.lower().endswith(".jpg")
					or dirfile.path.lower().endswith(".jpeg")
					or dirfile.path.lower().endswith(".png")
					or dirfile.path.lower().endswith(".gif")):
					wallpaper = Image.open(dirfile.path)
					imgDimension = wallpaper.size
					exifData = wallpaper.getexif()
					#https://jdhao.github.io/2019/07/31/image_rotation_exif_info/
					intOrientation = 1
					for key, val in exifData.items():
						if( key in ExifTags.TAGS and ExifTags.TAGS[key].lower() == "orientation" ):
							intOrientation = int(val)
					filebytesize = os.path.getsize(dirfile.path)
					sFilesize = kilo_mega_giga(filebytesize)
					kepfajlok.append( {"nev":dirfile.name,"utvonal":dirfile.path,"meret":sFilesize,"dimenzio":imgDimension,"orientacio":intOrientation} )
			print(f"{KIMENETFAJLNEV} összeállítása...")
			print(f"Útvonal: {OUTPUT_MD}")
			print(f"{len(kepfajlok)} képfájl található a gyűjteményben.")
			FilePointer = open(OUTPUT_MD,"w")
			print("Kimeneti fájl megnyitva.")
			FilePointer.write("# Háttérképek index fájl\n\n")
			FilePointer.write(f"###### {len(kepfajlok)} képfájl található a gyűjteményben.\n\n")
			FilePointer.write("Háttérkép|Adatok\n")
			FilePointer.write("---------|------\n")
			if( len(kepfajlok) > 0 ):
				kepfajlok.sort(key=lambda k: k.get('nev'))
				for kepfajl in kepfajlok:
					if( kepfajl["orientacio"] == 6 or kepfajl["orientacio"] == 8 ):
						sDimenzio= f"{kepfajl['dimenzio'][1]}*{kepfajl['dimenzio'][0]}"
					else:
						sDimenzio= f"{kepfajl['dimenzio'][0]}*{kepfajl['dimenzio'][1]}"
					FilePointer.write(f"<img src=\"./{kepfajl['nev']}\" width=\"{IMAGE_WIDTH}px\" height=\"auto\" alt=\"{kepfajl['nev']}\" />|*Fájlnév:* {kepfajl['nev']}<br/>*Méret:* {kepfajl['meret']}<br/>*Dimenzió:* {sDimenzio} pixel\n")
			else:
				FilePointer.write(" :confused: | *Nincsennek képfájlok!* ")
		except Exception as e:
			raise e
			return
		finally:
			if( FilePointer != None ):
				FilePointer.close()
				print("Kimeneti fájl lezárva.")
	else: #Ha a könyvtár nem létezik, akkor kilépünk hibaüzenettel.
		print_to_stderr(f"A(z) {WALLPAPERS_DIR} könyvtár nem létezik! [WALLPAPERS_DIR]")
		return

if __name__ == "__main__":
	if( ParancssorFeldolgozasa() == True ):
		KepekFeldolgozasa()
