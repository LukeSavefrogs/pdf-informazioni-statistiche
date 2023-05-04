import sys
from pathlib import Path
from typing import Dict, List, Literal

import PyPDF2

import pandas as pd

from rich.logging import RichHandler
import logging

logger = logging.getLogger("danea-easyfatt")
logger.addHandler(RichHandler(
    rich_tracebacks=True,
    omit_repeated_times=False,
    log_time_format="[%d-%m-%Y %H:%M:%S]"
))
logger.setLevel(logging.INFO)


def main():
	# Determine if application is a script file or frozen exe
	if getattr(sys, 'frozen', False):
		application_path = Path(sys.executable).parent
	elif __file__:
		application_path = Path(__file__).parent
	
	data: List[Dict] = []
	output_file = application_path / "output.xlsx"

	input_folder = Path(application_path / "data")
	if not input_folder.exists():
		logger.critical(f"Cartella '{input_folder}' inesistente. Crearla e riprovare.")
		return False

	input_files = list(input_folder.glob("*.pdf"))
	if not input_files:
		logger.critical(f"Nessun file PDF trovato nella cartella 'data'")
		return False

	# Read and parse all the files
	files_not_valid = []
	for file in input_files:
		try:
			file_data = parse_file(file)
		except:
			logger.warning(f"Formato file '{file}' non valido")
			files_not_valid.append(file)
			continue

		data.append({
			"Congregazione": file_data["info"]["congregazione"].title(),
			"Circoscrizione": file_data["info"]["circoscrizione"].title(),
			"Totale Proclamatori": file_data["info"]["proclamatori"],
			"Totale Pullman": file_data["1.Pullman"]["totale"],
			"Disabili - Sedia a ruote": file_data["2.Disabili"]["disabili_sedia"],
			"Disabili - Senza sedia a ruote": file_data["2.Disabili"]["disabili_no_sedia"],
			"Disabili - Problemi di udito": file_data["2.Disabili"]["problemi_udito"],
			"Disabili - Particolari necessità": file_data["2.Disabili"]["particolari_necessita"],
			"Disabili - Accompagnatori": file_data["2.Disabili"]["accompagnatori"],
			"Totale Disabili": file_data["2.Disabili"]["totale"],
			"Autovetture": file_data["3.Autovetture"]["no_invalidi"],
			"Autovetture - Disabili": file_data["3.Autovetture"]["invalidi"],
			"Totale Autovetture": file_data["3.Autovetture"]["totale"],
			"Totale Treno": file_data["4.Treno"]["totale"],
			"Totale Idonei Primo Soccorso": file_data["5.IdoneiPrimoSoccorso"]["totale"],
		})
	
	if files_not_valid:
		logger.info(f"Trovati {len(files_not_valid)} file non validi. Procedere manualmente")

	logger.debug("Inizio salvataggio")
	pd.DataFrame(data).to_excel(output_file, index=False)
	logger.info(f"Aggiornato file '{output_file}'")

	return True

def get_value(field, ret_type: Literal["raw", "boolean", "number", "text"] = "raw"):
	value = field["/V"] if "/V" in field.keys() else None
	
	if ret_type == "boolean":
		return True if value == "/1" else False
	elif ret_type == "number":
		return int(value) if value is not None else 0
	elif ret_type == "text":
		return str(value).strip() if value is not None else ""
	
	return value

def parse_file(file: Path):
	reader = PyPDF2.PdfReader(file, strict=False)
	fields = reader.get_fields()

	if get_value(fields["01.Congregazione"], "text").strip() == "" or get_value(fields["06.Num_Procl"], "text") == "":
		raise ValueError("File compilato non correttamente")

	return {
		"info": {
			"congregazione": get_value(fields["01.Congregazione"], "text"),
			"circoscrizione": get_value(fields["02.Circoscrizione"], "text"),
			"proclamatori": get_value(fields["06.Num_Procl"], "number"),
		},
		"1.Pullman": {
			"richiesto": get_value(fields["Pullman"], "boolean"),
			"totale": get_value(fields["07.Pullman_tot"], "number"),
			"altre_congregazioni": {
				"specificate": get_value(fields["08.PullmanAltreCongr"], "boolean"),
				"nomi": get_value(fields["09.Pullman_altre_congr"], "text"),
			},
			"sosta_fiera": get_value(fields["10.PullmanInSosta"], "boolean"),
			"capogruppo": {
				"nome": get_value(fields["03.Pullman_nome_capogruppo"], "text"),
				"email": get_value(fields["04.Pullman_email_capogruppo"], "text"),
				"telefono": get_value(fields["05.Pullman_telefono_capogruppo"], "text"),
			},
		},
		"2.Disabili": {
			"disabili_sedia": get_value(fields["11.Disabili_ruote"], "number"),
			"disabili_no_sedia": get_value(fields["12.Disabili_no_ruote"], "number"),
			"problemi_udito": get_value(fields["13.Problemi_udito"], "number"),
			"particolari_necessita": get_value(fields["14.Particolari_necessit\u00e0"], "number"),
			"accompagnatori": get_value(fields["15.Accompagnatori"], "number"),
			"totale": get_value(fields["16.Tot_disabili"], "number"),
		},
		"3.Autovetture": {
			"no_invalidi": get_value(fields["17.Autovetture"], "number"),
			"invalidi": get_value(fields["18.Autovetture_disabili"], "number"),
			"totale": get_value(fields["19.Tot_autovetture"], "number"),
		},
		"4.Treno": {
			"totale": get_value(fields["20.In_Treno"], "number"),
		},
		"5.IdoneiPrimoSoccorso": {
			"totale": get_value(fields["21.OperSanitari"], "number"),
		}
	}

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.exception("Eccezione inaspettata nella funzione main")
    finally:
        input("Premi [INVIO] per terminare il programma...")