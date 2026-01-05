from docx import Document
import pandas as pd

doc = Document("GlasgowWardsExtracted.docx")

all_tables = []

for table in doc.tables:
    for row in table.rows:
        all_tables.append([cell.text.strip() for cell in row.cells])

df = pd.DataFrame(all_tables)

df.to_csv("allwards.csv", index=False, header=False)
print("Saved all_tables.csv")
