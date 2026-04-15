"""Generate interactive HTML reports for agent execution."""

from datetime import datetime
from typing import Optional


class HTMLReportGenerator:
    """Generate beautiful HTML reports from agent execution."""

    def __init__(self, title: str = "kimi-code Analysis Report"):
        """Initialize report generator.

        Args:
            title: Report title
        """
        self.title = title
        self.sections = []
        self.metadata = {}

    def add_metadata(self, key: str, value: str) -> None:
        """Add metadata to report.

        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value

    def add_section(self, title: str, content: str, section_type: str = "text") -> None:
        """Add a section to the report.

        Args:
            title: Section title
            content: Section content
            section_type: Type of content (text, code, json, table)
        """
        self.sections.append(
            {
                "title": title,
                "content": content,
                "type": section_type,
            }
        )

    def add_code_block(self, title: str, code: str, language: str = "python") -> None:
        """Add a code block.

        Args:
            title: Block title
            code: Code content
            language: Programming language
        """
        self.sections.append(
            {
                "title": title,
                "content": code,
                "type": "code",
                "language": language,
            }
        )

    def add_table(self, title: str, headers: list[str], rows: list[list[str]]) -> None:
        """Add a table.

        Args:
            title: Table title
            headers: Column headers
            rows: Table rows (list of lists)
        """
        self.sections.append(
            {
                "title": title,
                "headers": headers,
                "rows": rows,
                "type": "table",
            }
        )

    def add_stats(self, stats: dict) -> None:
        """Add statistics panel.

        Args:
            stats: Dictionary of statistics
        """
        self.sections.append(
            {
                "title": "📊 Statistics",
                "stats": stats,
                "type": "stats",
            }
        )

    def generate(self, filename: Optional[str] = None) -> str:
        """Generate HTML report.

        Args:
            filename: Optional filename to save to

        Returns:
            HTML string
        """
        html = self._generate_html()

        if filename:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(html)

        return html

    def _generate_html(self) -> str:
        """Generate complete HTML document."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{self.title}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 20px;
            text-align: center;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}

        .metadata {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e0e0e0;
        }}

        .meta-item {{
            padding: 10px;
            background: white;
            border-radius: 5px;
            border-left: 4px solid #667eea;
        }}

        .meta-key {{
            font-weight: bold;
            color: #667eea;
            font-size: 0.9em;
        }}

        .meta-value {{
            color: #333;
            font-size: 1.1em;
            margin-top: 5px;
        }}

        .content {{
            padding: 40px 20px;
        }}

        .section {{
            margin-bottom: 40px;
            border-radius: 8px;
            overflow: hidden;
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
        }}

        .section-header {{
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            font-size: 1.3em;
            font-weight: bold;
        }}

        .section-body {{
            padding: 20px;
            background: white;
        }}

        .text-content {{
            line-height: 1.8;
            white-space: pre-wrap;
            word-wrap: break-word;
        }}

        .code-block {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }}

        th {{
            background: #667eea;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }}

        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }}

        tr:hover {{
            background: #f5f5f5;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 10px;
        }}

        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}

        .stat-label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 8px;
        }}

        .stat-value {{
            font-size: 2em;
            font-weight: bold;
        }}

        .footer {{
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            border-top: 1px solid #e0e0e0;
            color: #666;
            font-size: 0.9em;
        }}

        .success {{
            color: #28a745;
            font-weight: bold;
        }}

        .error {{
            color: #dc3545;
            font-weight: bold;
        }}

        .warning {{
            color: #ffc107;
            font-weight: bold;
        }}

        .info {{
            color: #17a2b8;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 {self.title}</h1>
            <p>Generated on {timestamp}</p>
        </div>

        {self._generate_metadata()}

        <div class="content">
            {self._generate_sections()}
        </div>

        <div class="footer">
            <p>Powered by <strong>kimi-code</strong> | AI-powered Python implementation of Claude Code</p>
        </div>
    </div>
</body>
</html>"""
        return html

    def _generate_metadata(self) -> str:
        """Generate metadata section."""
        if not self.metadata:
            return ""

        items = "\n".join(
            f"""        <div class="meta-item">
            <div class="meta-key">{key}</div>
            <div class="meta-value">{value}</div>
        </div>"""
            for key, value in self.metadata.items()
        )

        return f"""<div class="metadata">
{items}
        </div>"""

    def _generate_sections(self) -> str:
        """Generate content sections."""
        html = ""

        for section in self.sections:
            section_type = section.get("type", "text")
            title = section.get("title", "Section")

            html += f'        <div class="section">\n'
            html += f'            <div class="section-header">{title}</div>\n'
            html += f'            <div class="section-body">\n'

            if section_type == "text":
                content = section.get("content", "")
                html += f'                <div class="text-content">{self._escape_html(content)}</div>\n'

            elif section_type == "code":
                content = section.get("content", "")
                language = section.get("language", "python")
                html += f'                <div class="code-block">{self._escape_html(content)}</div>\n'

            elif section_type == "table":
                headers = section.get("headers", [])
                rows = section.get("rows", [])
                html += '                <table>\n'
                html += '                    <thead><tr>\n'
                for header in headers:
                    html += f'                        <th>{self._escape_html(header)}</th>\n'
                html += '                    </tr></thead>\n'
                html += '                    <tbody>\n'
                for row in rows:
                    html += '                        <tr>\n'
                    for cell in row:
                        html += f'                            <td>{self._escape_html(cell)}</td>\n'
                    html += '                        </tr>\n'
                html += '                    </tbody>\n'
                html += '                </table>\n'

            elif section_type == "stats":
                stats = section.get("stats", {})
                html += '                <div class="stats-grid">\n'
                for key, value in stats.items():
                    html += f"""                    <div class="stat-card">
                        <div class="stat-label">{key}</div>
                        <div class="stat-value">{value}</div>
                    </div>
"""
                html += '                </div>\n'

            html += '            </div>\n'
            html += '        </div>\n\n'

        return html

    @staticmethod
    def _escape_html(text: str) -> str:
        """Escape HTML special characters.

        Args:
            text: Text to escape

        Returns:
            Escaped text
        """
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;",
        }
        for char, escape in replacements.items():
            text = text.replace(char, escape)
        return text
