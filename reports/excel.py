"""
Excel report generation with formatting.
"""
import pandas as pd
from datetime import datetime
from typing import Dict
import xlsxwriter
from utils.logger import get_logger

logger = get_logger(__name__)


def create_excel_report(
    results: pd.DataFrame,
    output_path: str,
    screen_name: str,
    criteria: Dict = None,
    stats: Dict = None
):
    """
    Create a formatted Excel report with multiple sheets.

    Args:
        results: DataFrame with screening results
        output_path: Path for output file
        screen_name: Name of the screen
        criteria: Criteria used
        stats: Statistics dictionary
    """
    try:
        # Create Excel writer
        writer = pd.ExcelWriter(output_path, engine='xlsxwriter')
        workbook = writer.book

        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#4472C4',
            'font_color': 'white',
            'border': 1
        })

        title_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'bg_color': '#D9E1F2'
        })

        number_format = workbook.add_format({'num_format': '#,##0.00'})
        percent_format = workbook.add_format({'num_format': '0.00%'})
        currency_format = workbook.add_format({'num_format': '₹#,##0'})

        # Green for good metrics
        good_format = workbook.add_format({
            'bg_color': '#C6EFCE',
            'font_color': '#006100'
        })

        # Red for concerning metrics
        bad_format = workbook.add_format({
            'bg_color': '#FFC7CE',
            'font_color': '#9C0006'
        })

        # Sheet 1: Summary
        summary_sheet = workbook.add_worksheet('Summary')
        summary_sheet.write('A1', f'{screen_name} - Screening Results', title_format)
        summary_sheet.write('A2', f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')

        row = 4
        if stats:
            summary_sheet.write(row, 0, 'Statistics', title_format)
            row += 1
            summary_sheet.write(row, 0, 'Total Stocks:')
            summary_sheet.write(row, 1, stats.get('total_stocks', 0))
            row += 1
            if stats.get('avg_roe'):
                summary_sheet.write(row, 0, 'Average ROE:')
                summary_sheet.write(row, 1, f"{stats['avg_roe']:.2f}%")
                row += 1
            if stats.get('median_pb'):
                summary_sheet.write(row, 0, 'Median P/B:')
                summary_sheet.write(row, 1, stats['median_pb'], number_format)
                row += 1
            if stats.get('median_de'):
                summary_sheet.write(row, 0, 'Median D/E:')
                summary_sheet.write(row, 1, stats['median_de'], number_format)

        row += 2
        if criteria:
            summary_sheet.write(row, 0, 'Screening Criteria', title_format)
            row += 1
            for field, condition in criteria.items():
                field_display = field.replace('_', ' ').title()
                operator = condition['operator']
                value = condition.get('value', '')
                summary_sheet.write(row, 0, field_display)
                summary_sheet.write(row, 1, f"{operator} {value}")
                row += 1

        # Sheet 2: Results
        results.to_excel(writer, sheet_name='Results', index=False)
        results_sheet = writer.sheets['Results']

        # Format header row
        for col_num, value in enumerate(results.columns.values):
            results_sheet.write(0, col_num, value, header_format)

        # Apply conditional formatting
        if 'roe' in results.columns:
            roe_col = results.columns.get_loc('roe')
            results_sheet.conditional_format(1, roe_col, len(results), roe_col, {
                'type': 'cell',
                'criteria': '>',
                'value': 20,
                'format': good_format
            })

        if 'debt_equity' in results.columns:
            de_col = results.columns.get_loc('debt_equity')
            results_sheet.conditional_format(1, de_col, len(results), de_col, {
                'type': 'cell',
                'criteria': '>',
                'value': 2,
                'format': bad_format
            })

        # Adjust column widths
        for idx, col in enumerate(results.columns):
            max_len = max(
                results[col].astype(str).apply(len).max(),
                len(col)
            ) + 2
            results_sheet.set_column(idx, idx, min(max_len, 30))

        # Sheet 3: Sector Analysis
        if stats and stats.get('sectors'):
            sector_df = pd.DataFrame(
                list(stats['sectors'].items()),
                columns=['Sector', 'Count']
            )
            sector_df = sector_df.sort_values('Count', ascending=False)
            sector_df.to_excel(writer, sheet_name='Sector Analysis', index=False)

            sector_sheet = writer.sheets['Sector Analysis']
            for col_num, value in enumerate(sector_df.columns.values):
                sector_sheet.write(0, col_num, value, header_format)

        # Close writer
        writer.close()

        logger.info(f"Excel report created: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error creating Excel report: {str(e)}")
        return False
