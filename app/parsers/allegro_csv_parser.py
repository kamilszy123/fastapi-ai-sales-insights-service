import csv

from app.exceptions.parser_exceptions import CSVValidationError


class AllegroCSVParser:
    def parse(self, csv_file_stream) -> dict:
        tables = []
        current_table = []
        headers = None
        csv_reader = csv.reader(csv_file_stream)

        for row in csv_reader:
            # if row is empty this is the end of current table
            if not row:
                if current_table:
                    tables.append(current_table)
                    current_table = []
                    headers = None
                continue
            # beginning of new table
            if headers is None:
                headers = row
                continue

            current_table.append(dict(zip(headers, row)))

        if current_table:
            tables.append(current_table)

        result = {}

        for table in tables:
            table_type = table[0]["Type"]

            if table_type == "order":
                result["orders"] = table

            elif table_type == "lineItem":
                result["order_items"] = table

            elif table_type == "summary":
                result["summary"] = table[0]

        required_sections = [
            "orders",
            "order_items",
            "summary",
        ]
        for section in required_sections:
            if section not in result:
                raise CSVValidationError(f"Missing required section: {section}")

        return result
