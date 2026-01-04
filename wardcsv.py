import tabula
import pandas as pd

pdf_path = "viewSelectedDocument.pdf"

# Step 1: Extract all tables
tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True, lattice=True)

# Step 2: Combine all tables into a single DataFrame
all_data = pd.DataFrame()
for table in tables:
    all_data = pd.concat([all_data, table], ignore_index=True)

# Step 3: Determine ward name for filename
# Assuming the first column contains ward names
# Take the first non-empty value from the first column
ward_name = str(all_data.iloc[0, 0]).replace(" ", "_")  # replace spaces with underscores

# Step 4: Save combined table to CSV without headers
all_data.to_csv(f"{ward_name}.csv", index=False, header=False)
print(f"Saved combined table as {ward_name}.csv")


