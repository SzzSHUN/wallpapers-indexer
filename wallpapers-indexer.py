#!/bin/env python
# vim: ts=4:sw=4:sts=4:noet:ai

# Verzió: 20210407.2110

import sys
import os
import subprocess

WALLPAPERS_DIR="../Wallpapers"
OUTPUT_MD=f"{WALLPAPERS_DIR}/INDEX.md"
#identify -format "%wx%h" [imagemagick]

#Üzenet kiírása a standard hibakimenetre
def print_to_stderr(*szoveg):
	print(*szoveg, file = sys.stderr)

#Üzenet kiírása a standard kimenetre
def print_to_stdout(*szoveg):
	print(*szoveg, file = sys.stdout)

#Main
def main():
	NormInputDir = os.path.normpath( WALLPAPERS_DIR )
	print(NormInputDir)
	#Ellenőrizzük a WALLPAPERS_DIR globális változóban megadott könyvtár meglétét.
	if( os.path.isdir(NormInputDir) == True ):
		#Ha a könyvtár létezik, akkor megnézzük, hogy a szükséges programcsomag telepítve van-e
		if( os.path.isfile("/usr/bin/identify") or os.path.isfile("/bin/identify")):
			#A program telepítve van, most végigjárjuk a könyvtár képeit és kiírjuk az adatokat az OUTPUT_MD változó által meghatározott fájlba.
			NormOutFile = os.path.normpath(OUTPUT_MD)
			print(NormOutFile)
			FilePointer = None
			try:
				FilePointer = open(NormOutFile,"w")
				FilePointer.write("## Háttérképek indexfájl\n\n")
				FilePointer.write("Háttérkép|Adatok\n")
				FilePointer.write("---------|------\n")
				kepfajlok= [] 
				for dirfile in os.scandir(path=NormInputDir):
					if( dirfile.path.lower().endswith(".jpg")
						or dirfile.path.lower().endswith(".jpeg")
						or dirfile.path.lower().endswith(".png")
						or dirfile.path.lower().endswith(".gif")):
						print(f"Feldolgozás: {dirfile.name}")
						imgDimension = subprocess.run(["identify","-format","%wx%h",dirfile.path], capture_output=True,text=True).stdout
						filebytesize = os.path.getsize(dirfile.path)
						kepfajlok.append( {"nev":dirfile.name,"utvonal":dirfile.path,"meret":filebytesize,"dimenzio":imgDimension} )
				kepfajlok.sort(key=lambda k: k.get('nev'))
				for kepfajl in kepfajlok:
					print(f"Kiírás: {kepfajl['nev']}")
					FilePointer.write(f"<img src=\"./{kepfajl['nev']}\" width=\"250px\" height=\"auto\" alt=\"{kepfajl['nev']}\" />|*{kepfajl['nev']}*<br/>Méret: {kepfajl['meret']}<br/>Dimenzió: {kepfajl['dimenzio']} pixel\n")
			except Exception as e:
				#print_to_stderr(f"{e}")
				raise e
				return
			finally:
				if( FilePointer != None ):
					FilePointer.close()
		else: #Az imagemagick csomag nincs telepítve, hibaüzenettel kilépünk
			print_to_stderr("Az imagemagick csomag nincs telepítve, nem tudom használni az identify programot.")
			return			
	else: #Ha a könyvtár nem létezik, akkor kilépünk hibaüzenettel.
		print_to_stderr(f"A(z) {NormInputDir} könyvtár nem létezik! [WALLPAPERS_DIR]")
		return

if __name__ == "__main__":
	main();
