class LatexTableUtil:
    '''
    dimY \ dimX | 1 | 2 | ... | dimX (header)
    --------------------------------
    1           |   |   |     |
    2           |   |   |     |
    ...         |   |   |     |
    dimY        |   |   |     |
    (row header)
    '''

    DEFAULT_OPTIONS = {
        "table_border": True,
        "row_hline": True,  
        "default_centering": "c",
        "has_header": True,
        "header_bold": True,
        "header_centering": "l",
        "header_hline": True,
        "has_row_header": True,
        "row_header_bold": True,
        "row_header_centering": "l",
        "row_header_vline": True,
    }

    def __init__(self, rows, name = "Table", options={}):
        self.rows = rows
        self.name = name
        self.dimY = len(rows)
        self.dimX = len(rows[0])
        self.options = {**LatexTableUtil.DEFAULT_OPTIONS, **options}

    @staticmethod
    def create_from_csv(csv_file: str, options={}):
        with open(csv_file, "r") as f:
            rows = []
            for line in f.readline():
                rows.append(line.replace("\n","").strip().split(","))
            return LatexTableUtil(rows, options)

    def to_latex(self):
        str_table = []
        start_row_index = 0

        # Default Formatted Table
        str_table.append(f"%----{self.name}\n")
        str_table.append("\\begin{table}[h!]\n\\begin{center}\n")

        # Output to latex table
        hline = "\\hline\n"

        # Formatting Header
        cols = [ self.options["default_centering"] for _ in range(self.dimY + 1)]
        cols[0] = self.options["header_centering"]
        if self.options["table_border"]:
            cols[0] = " | " + cols[0]
            cols[-1] = cols[-1] + " | "

        cols_header = " | ".join(cols) + " | "
        str_table.append("\\begin{tabular}{ " + cols_header + " }")

        # Header
        header = ""
        if self.options["has_header"]:
            header = " & ".join(self.rows[0]) + " \\\\\n"
            start_row_index = 1
            if self.options["header_hline"]:
                str_table.append(hline)
            str_table.append(header)
            if self.options["header_hline"]:
                str_table.append(hline)

        # Rows
        for row_index in range(start_row_index, self.dimY):
            row = [str(value) for value in self.rows[row_index]]            
            str_table.append(" & ".join(row) + " \\\\\n")
            if self.options["row_hline"]:
                str_table.append(hline)

        # End
        str_table.append("\\end{tabular}\n\\end{center}\n\\caption{" + self.name + " table to test captions and labels.}\n\\label{table:1}\n\\end{table}")
        return "".join(str_table)