import re
import requests
from pathlib import Path
import genanki
import tqdm
import json
import sys

CLEANR = re.compile('<.*?>') 

# def base_url(word, number=1):
# 	letter = word[0]	
# 	return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{letter}/{word.ljust(5, '0')}{number:03}.mp3"

def base_url(word, filename):
	letter = word[0]	
	return f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{letter}/{filename}"


def cleanhtml(raw_html):
  cleantext = re.sub(CLEANR, '', raw_html)
  return cleantext


def cleanword(word):
	prefix = "to "
	if word.startswith(prefix):
		return word[len(prefix):]
	else:
		return word  

		
with open("input.json", "r") as fp:
	rows = json.load(fp,)

# outrows=[]
# for row in rows:
# 	french = row["french"]
# 	infinitive =  row["infinitive"]["text"]
# 	preterite = row["preterite"]["text"]
# 	pastparticipe = row["pastparticipe"]["text"]
# 	filename1 = base_url(cleanword(infinitive), 1).split("/")[-1]
# 	filename2 = base_url(cleanword(infinitive), 2).split("/")[-1]
# 	outrows.append({
# 				"french":french, 
#  				"infinitive": {"text": infinitive, "mwid":filename1},
#  				"preterite": {"text": preterite, "mwid":filename2},
#  				"pastparticipe": {"text": pastparticipe, "mwid":filename2},
# 	})

# with open("output.json", "w") as fp:
# 	json.dump(outrows, fp, indent=2)

# sys.exit(0)

TEST_MODEL = genanki.Model(
  234567, 'irregular verbs',
  fields=[
    {
      'name': 'french',
    },
    {
      'name': 'infinitive',
    },
    {
      'name': 'preterite',
    },
    {
      'name': 'pastparticipe',
    },
  ],
  templates=[
    {
      'name': 'card1',
      'qfmt': '{{french}}',
      'afmt': '{{FrontSide}}'
              '<hr id="infinitive">'
              '{{infinitive}}'
              '<hr id="preterite">'
              '{{preterite}}'
              '<hr id="pastparticipe">'
              '{{pastparticipe}}',
    }
  ],
)

deck = genanki.Deck(11122009, 'irregular verbs')

media_files = []

Path("sounds").mkdir(parents=True, exist_ok=True)



output_words = []

for row in tqdm.tqdm(rows):
	print(row)
	french = row["french"]
	infinitive =  row["infinitive"]["text"]

	output_row = [french]
	#for ix, word in enumerate([infinitive, preterite, pastparticipe]):
	for d in ['infinitive', 'preterite', 'pastparticipe']:
		word = row[d]['text']
		ix = row[d]['mwid']
		cleaned_word = cleanword(cleanhtml(infinitive))
		url = base_url(cleaned_word, filename=ix)
		
		output_filename = url.split("/")[-1]
		
		output_file = f"sounds/{output_filename}"
		if output_file not in media_files:
						
			response = requests.get(url)
			with open(output_file, "wb") as fp:
				fp.write(response.content)
			media_files.append(output_file)
		print(word)
		output_row.append(f"{word} [sound:{output_filename}]")
	output_words.append(output_row)


print(media_files)
for note_word in output_words:
	note = genanki.Note(TEST_MODEL, note_word)
	deck.add_note(note)
genanki.Package(deck, media_files=media_files).write_to_file("irregular-verbs.apkg")
