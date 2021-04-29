#!/bin/env python
# vim: ts=4:sw=4:sts=4:noet:ai
# Készítette a PingvinSarok közösség számára:
# SzzS (info [kukac] szarkazsolt [pont] hu)

import sys
import os
import getopt
import PIL
from PIL import Image, ExifTags

SCRIPTNEV="wallpapers-indexer.py"
SCRIPTVERZIO="20210428.1829"

#Globális változók értékének feltöltése az lapértelmezésekkel
WALLPAPERS_DIRPATH="."
THUMBIMAGES_DIRNAME=".thumbs"
THUMBIMAGES_DIRPATH=f"{WALLPAPERS_DIRPATH}/{THUMBIMAGES_DIRNAME}"
KIMENETFAJLNEV="INDEX.md"
OUTPUT_MD=f"{WALLPAPERS_DIRPATH}/{KIMENETFAJLNEV}"
THUMBNAIL_WIDTH=150
THUMBNAIL_WIDTH_MIN=50
THUMBNAIL_WIDTH_MAX=600

#Üzenet kiírása a standard hibakimenetre
def hibakiiras(*szoveg):
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
	global SCRIPTNEV,OUTPUT_MD, WALLPAPERS_DIRPATH, KIMENETFAJLNEV, THUMBNAIL_WIDTH
	global THUMBIMAGES_DIRNAME, THUMBIMAGES_DIRPATH
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
				WALLPAPERS_DIRPATH = arg.rstrip('/ ')
			elif( opt == "--kimenet" ):
				KIMENETFAJLNEV = arg.strip()
			elif( opt == "--kepszelesseg" ):
				THUMBNAIL_WIDTH = arg if arg.isnumeric() else THUMBNAIL_WIDTH
			elif( opt == "--belyeg" ):
				THUMBIMAGES_DIRNAME= arg.rstrip('/ ')
	THUMBIMAGES_DIRPATH=f"{WALLPAPERS_DIRPATH}/{THUMBIMAGES_DIRNAME}"
	OUTPUT_MD=f"{WALLPAPERS_DIRPATH}/{KIMENETFAJLNEV}"
	return bResult

#Súgó szöveg kiírása
def ParancssorSugo():
	print(f"""Név: {SCRIPTNEV}
Verzió: {SCRIPTVERZIO}
Leírás: PingvinSarok közösség Wallpapers repójának indexelője
Használat:{SCRIPTNEV} [PARAMÉTEREK]

Paraméterek:
	--kepek
		Háttérképfájlokat tartalmazó könyvtár útvonalának megadása.
		Ha nincs megadva, akkor az aktuális köyvtár lesz beállítva

	--kimenet
		A kimeneti fájl neve
		Ha nincs megadva, akkor {KIMENETFAJLNEV}

	--kepszelesseg
		A táblázatban megjelenő index kép szélessége pixelben.
		Az alapértelmezett érték: {THUMBNAIL_WIDTH} 
	
	--belyeg
		A bélyegképek tárolására szolgáló könyvtár neve.
		A könyvtár a háttérkép fájlokat tartalmazó mappán belül kerül létrehozásra.
		Alapértelmezett érték: {THUMBIMAGES_DIRNAME}

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
	print(SCRIPTVERZIO)

# Program paraméterváltozók értékeinek ellenőrzése, javítása
def ValtozokEllenorzese():
	global WALLPAPERS_DIRPATH, THUMBIMAGES_DIRNAME, THUMBNAIL_WIDTH
	if( len(WALLPAPERS_DIRPATH)==0 ):
		WALLPAPERS_DIRPATH="."
	if( len(THUMBIMAGES_DIRNAME)==0 ):
		THUMBIMAGES_DIRNAME = ".thumbs"
	THUMBNAIL_WIDTH = min(THUMBNAIL_WIDTH_MAX,max(THUMBNAIL_WIDTH_MIN,THUMBNAIL_WIDTH))
	#A bélyegkép könyvtár meglétének ellenőrzése, létrehozása
	if( os.path.isdir(THUMBIMAGES_DIRPATH) == False ):
		os.mkdir(THUMBIMAGES_DIRPATH)

#Thumbnail fájl nevét adja vissza az eredeti fájlnév alapján.
#Bemenet: A háttérkép fájl neve, útvonal nélkül.
def GetThumbFileName(eredeti):
	return f"t@{eredeti}"

#A Thumbfájl útvonalát állítja össze az eredeti fájl alapján.
#Bemenet: A háttérkép fájl útvonala
#Kimenet: A háttérkép fájlhoz tartozó bélyegkép útvonala, vagy hiba esetén None.
def GetThumbFilePath(eredeti):
	bontott=os.path.split(eredeti)
	sUtvonal=bontott[0].rstrip('/')
	sFajlnev=bontott[1] if len(bontott[1])>0 else None
	if( sFajlnev != None ):
		if( os.path.isdir(sUtvonal) ):
			sResult="{0}/{1}/{2}".format(sUtvonal,THUMBIMAGES_DIRNAME,GetThumbFileName(sFajlnev))
		else:
			sResult=None
			hibakiiras(f"GetThumbFilePath: '{sUtvonal}' nem könyvtár [{eredeti}].")
	else:
		sResult=None
		hibakiiras(f"GetThumbFilePath: sFajlnev=None [{eredeti}].")
	return sResult

#Van-e már bélyegkép az adott háttérkép fájlhoz?
#Bemenet: A vizsgálandó háttérkép fájl útvonala
#Kimenet: True ha van, False ha nincs
def BelyegkepVan(eredeti):
	return True if os.path.isfile(GetThumbFilePath(eredeti)) else False

#A bélyegkép méreteinek kiszámítása
#Bemenet: szélesség, magasság, orientáció
#Kimenet: A bélyegkép mérete. Tömb. [0]-szélesség [1]-magasság
def ComputeBelyegkepSize(szelesseg, magassag, orientacio=1):
	imageWidth=magassag if orientacio==6 or orientacio==8 else szelesseg
	imageHeight=szelesseg if orientacio==6 or orientacio==8 else magassag
	fPercent=float(THUMBNAIL_WIDTH/(imageWidth/100))
	aSize=[0,0]
	if( orientacio == 6 or orientacio == 8):
		aSize = [int(float(imageHeight/100*fPercent)),THUMBNAIL_WIDTH]
	else:
		aSize = [THUMBNAIL_WIDTH,int(float(imageHeight/100*fPercent))]
	return aSize

#Bélyegkép készítése és mentése
#Bemenet: A betöltött Wallpaper képet tartalmazó objektum
def CreateBelyegkep(imgSource):
	bResult = True
	try:
		exifData = imgSource.getexif()
		intOrientation = 1
		for key, val in exifData.items():
			if( key in ExifTags.TAGS and ExifTags.TAGS[key].lower() == "orientation" ):
				intOrientation = int(val)
		if( intOrientation == 8 ):
			thumbImage = imgSource.rotate(90, PIL.Image.NEAREST, expand=1)
		elif( intOrientation == 3 ):
			thumbImage = imgSource.rotate(180, PIL.Image.NEAREST, expand=1)
		elif( intOrientation == 6 ):
			thumbImage = imgSource.rotate(-90, PIL.Image.NEAREST, expand=1)
		else:
			thumbImage = imgSource.copy()
		belyegSize = ComputeBelyegkepSize(thumbImage.size[0], thumbImage.size[1], 1)
		belyegPath = GetThumbFilePath(imgSource.filename)
		thumbImage = thumbImage.resize( (belyegSize[0],belyegSize[1]) )
		thumbImage.save(belyegPath)
	except Exception as e:
		bResult = False
		raise e
	return bResult

#Háttérkép fájl nevét adja vissza a bélyegkép fájlnév alapján.
#Bemenet: A bélyegkép fájl neve, útvonal nélkül.
def GetWallpaperFileName(belyegkep):
	return belyegkep.replace("t@","",1)

#A háttérkép fájl útvonalát állítja össze a bélyegkép fájl alapján.
#Bemenet: A bélyegkép fájl útvonala
#Kimenet: A bélyegképhez tartozó háttérkép útvonala, vagy hiba esetén None
def GetWallpaperFilePath(belyegkep):
	bontott=os.path.split(belyegkep)
	sUtvonal=bontott[0].rstrip('/')
	sFajlnev=bontott[1] if len(bontott[1])>0 else None
	if( sFajlnev != None ):
		if( os.path.isdir(sUtvonal) ):
			sResult = belyegkep.replace(f"{THUMBIMAGES_DIRNAME}/","",1).replace("t@","")
		else:
			hibakiiras(f"GetWallpaperFilePath: '{sUtvonal}' nem könyvtár [{belyegkep}].")
			sResult=None
	else:
		sResult=None
		hibakiiras(f"GetWallpaperFilePath: sFajlnev=None [{belyegkep}].")
	#print(f"GetWallpaperFilePath result: {sResult}")
	return sResult

#Tartozik-e háttérkép fájl a megadott bélyegképhez
#Bemenet: A bélyegkép fájl útvonala
#Kimenet: A bélyegképhez társított háttérkép fájl létezik: True, nem létezik: False
def HatterkepVan(belyegkep):
	return True if os.path.isfile(GetWallpaperFilePath(belyegkep)) else False

#Bélyegképek ellenőrzése
#Ha az adott bélyegképhez nem tartozik háttérkép, akkor törölni kell.
def BelyegkepEllenorzo():
	if( os.path.isdir(THUMBIMAGES_DIRPATH) == True ):
		torlendobelyeg=[]
		for dirfile in os.scandir(path=THUMBIMAGES_DIRPATH):
			#print("Bélyegkép: {}".format(dirfile.path.lower()))
			if( "t@" in dirfile.path.lower() ):
				if( HatterkepVan(dirfile.path) == False ):
					torlendobelyeg.append(dirfile.path)
		print("{0}db törlendő bélyegkép van.".format(len(torlendobelyeg)))
		if( len(torlendobelyeg) > 0 ):
				for torlendo in torlendobelyeg:
					try:
						print(f"Bélyegkép törlése: {torlendo}")
						os.remove(torlendo)
					except OSError as ose:
						hibakiiras(f"A {torlendo} fájl törlése hibát okozott:")
						hibakiiras(e)
				print("Elárvult bélyegképek törlése megtörtént.")
	else:
		hibakiiras(f"A(z) {THUMBIMAGES_DIRPATH} könyvtár nem létezik! [THUMBIMAGES_DIRPATH]")

#Képek feldolgozása
def KepekFeldolgozasa():
	print(f"Képfájlok könyvtára: {WALLPAPERS_DIRPATH}")
	print(f"Bélyegképek könyvtára: {THUMBIMAGES_DIRPATH}")
	print(f"Bélyegképek szélessége: {THUMBNAIL_WIDTH}px")
	print(f"Kimeneti fájl: {OUTPUT_MD}")

	#Ellenőrizzük a WALLPAPERS_DIRPATH globális változóban megadott könyvtár meglétét.
	if( os.path.isdir(WALLPAPERS_DIRPATH) == True ):
		#Ha a könyvtár létezik, akkor végigjárjuk a könyvtár képeit és kiírjuk az adatokat az OUTPUT_MD változó által meghatározott fájlba.
		FilePointer = None
		kepfajlok = []
		try:
			print("Képek feldolgozása...")
			for dirfile in os.scandir(path=WALLPAPERS_DIRPATH):
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
					CreateBelyegkep(wallpaper)
					kepfajlok.append( {"nev":dirfile.name,"utvonal":dirfile.path,"meret":sFilesize,"dimenzio":imgDimension,"orientacio":intOrientation} )
			print(f"{KIMENETFAJLNEV} összeállítása...")
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
					FilePointer.write(f"<img src=\"{GetThumbFilePath(kepfajl['utvonal'])}\" width=\"{THUMBNAIL_WIDTH}px\" height=\"auto\" alt=\"{kepfajl['nev']}\" />|*Fájlnév:* <a href=\"{kepfajl['utvonal']}\">{kepfajl['nev']}</a><br/>*Méret:* {kepfajl['meret']}<br/>*Dimenzió:* {sDimenzio} pixel\n")
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
		hibakiiras(f"A(z) {WALLPAPERS_DIRPATH} könyvtár nem létezik! [WALLPAPERS_DIRPATH]")
		return

if __name__ == "__main__":
	if( ParancssorFeldolgozasa() == True ):
		ValtozokEllenorzese()
		KepekFeldolgozasa()
		BelyegkepEllenorzo()
