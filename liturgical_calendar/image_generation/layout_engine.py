from typing import Any, Dict, List


class LayoutEngine:
    """
    Responsible for calculating layout positions and text for each section of the liturgical image.
    Does not draw to an image; returns layout data for use by an image builder.
    """

    def create_header_layout(
        self,
        season: str,
        date: str,
        fonts: Dict[str, Any],
        draw: Any,
        width: int,
        padding: int,
        font_manager=None,
    ) -> Dict[str, Any]:
        """Return layout info for the header row (season, dash, date)."""
        # Fonts expected: {'sans_uc': ..., 'serif': ...}
        season_text = season.upper()
        header_dash = " — "
        date_text = date
        sans_font_36_uc = fonts["sans_uc"]
        serif_font_36 = fonts["serif"]
        # Measure for baseline alignment
        if font_manager:
            season_w, season_h = font_manager.get_text_size(
                season_text, sans_font_36_uc
            )
            dash_w, dash_h = font_manager.get_text_size(header_dash, sans_font_36_uc)
            date_w, date_h = font_manager.get_text_size(date_text, serif_font_36)
        else:
            season_w, season_h = sans_font_36_uc.getbbox(season_text)[2:4]
            dash_w, dash_h = sans_font_36_uc.getbbox(header_dash)[2:4]
            date_w, date_h = serif_font_36.getbbox(date_text)[2:4]
        total_w = season_w + dash_w + date_w
        x = (width - total_w) // 2
        y = padding
        # Baseline alignment: get font metrics
        sans_ascent, sans_descent = sans_font_36_uc.getmetrics()
        serif_ascent, serif_descent = serif_font_36.getmetrics()
        baseline_y = y + max(sans_ascent, serif_ascent)
        return {
            "season": {
                "text": season_text,
                "font": sans_font_36_uc,
                "pos": (x, baseline_y - sans_ascent),
            },
            "dash": {
                "text": header_dash,
                "font": sans_font_36_uc,
                "pos": (x + season_w, baseline_y - sans_ascent),
            },
            "date": {
                "text": date_text,
                "font": serif_font_36,
                "pos": (x + season_w + dash_w, baseline_y - serif_ascent),
            },
            "baseline_y": baseline_y,
            "height": max(season_h, dash_h, date_h),
        }

    def create_artwork_layout(
        self,
        artwork: Dict[str, Any],
        next_artwork: Dict[str, Any],
        width: int,
        art_size: int,
        y: int,
        fonts: Dict[str, Any] = None,
        next_title_y_offset: int = 16,
        draw: Any = None,
        font_manager=None,
    ) -> Dict[str, Any]:
        """
        Return layout info for the artwork and (optionally) next artwork thumbnail and its text.
        """
        art_x = (width - art_size) // 2
        layout = {
            "main": {
                "pos": (art_x, y),
                "size": (art_size, art_size),
                "artwork": artwork,
            },
            "show_next": False,
        }
        if next_artwork and fonts and font_manager:
            thumb_size = art_size // 2
            thumb_x = art_x + (art_size - thumb_size) // 2
            thumb_y = y + (art_size - thumb_size) // 2
            layout["next"] = {
                "pos": (thumb_x, thumb_y),
                "size": (thumb_size, thumb_size),
                "artwork": next_artwork,
            }
            # Add next artwork label/title/date layout
            layout.update(
                self._create_next_artwork_layout(
                    next_artwork,
                    art_x,
                    art_size,
                    thumb_y,
                    thumb_size,
                    fonts,
                    next_title_y_offset,
                    None,
                    font_manager,
                )
            )
            layout["show_next"] = True
        return layout

    def _get_text_width(self, draw, text, font, font_manager=None):
        if font_manager:
            return font_manager.get_text_size(text, font)[0]
        return font.getbbox(text)[2] - font.getbbox(text)[0]

    def _create_next_artwork_layout(
        self,
        next_artwork: Dict[str, Any],
        art_x: int,
        art_size: int,
        thumb_y: int,
        thumb_size: int,
        fonts: Dict[str, Any],
        next_title_y_offset: int,
        draw: Any,
        font_manager=None,
    ) -> Dict[str, Any]:
        """
        Return layout info for the 'NEXT:' label, next artwork title, and date below the thumbnail.
        """
        next_prefix = "NEXT: "
        next_title = next_artwork.get("name", "")
        sans_font = fonts["sans"]
        serif_font = fonts["serif"]
        # Baseline alignment
        sans_ascent, _ = sans_font.getmetrics()
        serif_ascent, _ = serif_font.getmetrics()
        next_prefix_w = self._get_text_width(None, next_prefix, sans_font, font_manager)
        next_title_w = self._get_text_width(None, next_title, serif_font, font_manager)
        total_next_w = next_prefix_w + next_title_w
        next_x = art_x + (art_size - total_next_w) // 2
        next_title_y = thumb_y + thumb_size + next_title_y_offset
        baseline_y = next_title_y + max(sans_ascent, serif_ascent)
        layout = {
            "next_label": {
                "text": next_prefix,
                "font": sans_font,
                "pos": (next_x, baseline_y - sans_ascent),
            },
            "next_title": {
                "text": next_title,
                "font": serif_font,
                "pos": (next_x + next_prefix_w, baseline_y - serif_ascent),
            },
        }
        # Date below the next artwork title
        next_artwork_date = next_artwork.get("date").upper()
        if next_artwork_date:
            date_text = next_artwork_date
            sans_font_26 = fonts.get("sans_26", fonts.get("sans_32", sans_font))
            date_x = next_x + next_prefix_w
            date_y = baseline_y + 8  # 8px below the title
            layout["next_date"] = {
                "text": date_text,
                "font": sans_font_26,
                "pos": (date_x, date_y),
            }
        return layout

    def create_title_layout(
        self,
        title: str,
        fonts: Dict[str, Any],
        draw: Any,
        width: int,
        padding: int,
        title_font_size: int,
        title_line_height: float,
        start_y: int,
        font_manager=None,
    ) -> Dict[str, Any]:
        """Return layout info for the artwork title, including wrapped lines and positions."""
        font = fonts["serif_96"]
        max_width = width - 2 * padding

        # Wrap text
        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            current = ""
            for word in words:
                test = current + (" " if current else "") + word
                w = (
                    font_manager.get_text_size(test, font)[0]
                    if font_manager
                    else font.getbbox(test)[2] - font.getbbox(test)[0]
                )
                if w <= max_width:
                    current = test
                else:
                    if current:
                        lines.append(current)
                    current = word
            if current:
                lines.append(current)
            return lines

        lines = wrap_text(title, font, max_width)
        layout_lines = []
        last_baseline = start_y
        for i, line in enumerate(lines):
            line_w = (
                font_manager.get_text_size(line, font)[0]
                if font_manager
                else font.getbbox(line)[2] - font.getbbox(line)[0]
            )
            line_x = (width - line_w) // 2
            line_y = start_y + i * int(title_font_size * title_line_height)
            layout_lines.append({"text": line, "font": font, "pos": (line_x, line_y)})
            ascent = (
                font_manager.get_text_metrics(font)[0]
                if font_manager
                else font.getmetrics()[0]
            )
            last_baseline = line_y + ascent  # baseline = y + ascent
        return {"lines": layout_lines, "last_baseline": last_baseline}

    def create_readings_layout(
        self,
        week: str,
        readings: list,
        fonts: Dict[str, Any],
        draw: Any,
        width: int,
        padding: int,
        start_y: int,
        line_height: int,
        font_manager=None,
    ) -> Dict[str, Any]:
        """Return layout info for the week and readings columns, including vertical line and last baseline y."""
        sans_uc = fonts["sans_uc"]
        serif = fonts["serif"]
        # Calculate widths
        week_w = (
            font_manager.get_text_size(week, sans_uc)[0]
            if font_manager
            else sans_uc.getbbox(week)[2] - sans_uc.getbbox(week)[0]
        )
        readings_w = 0
        for r in readings:
            w = (
                font_manager.get_text_size(r, serif)[0]
                if font_manager
                else serif.getbbox(r)[2] - serif.getbbox(r)[0]
            )
            readings_w = max(readings_w, w)
        col_gap = 28 * 2 + 1  # 28px padding each side + 1px line
        total_cols_w = week_w + col_gap + readings_w
        col1_x = (width - total_cols_w) // 2
        col2_x = col1_x + week_w + col_gap
        # Baseline alignment
        sans_ascent_col = (
            font_manager.get_text_metrics(sans_uc)[0]
            if font_manager
            else sans_uc.getmetrics()[0]
        )
        serif_ascent_col = (
            font_manager.get_text_metrics(serif)[0]
            if font_manager
            else serif.getmetrics()[0]
        )
        col_baseline_y = start_y + max(sans_ascent_col, serif_ascent_col)
        # Layout for week
        week_layout = {
            "text": week,
            "font": sans_uc,
            "pos": (col1_x, col_baseline_y - sans_ascent_col),
        }
        # Layout for readings
        readings_layout = []
        reading_y = col_baseline_y - serif_ascent_col
        for r in readings:
            readings_layout.append(
                {"text": r, "font": serif, "pos": (col2_x, reading_y)}
            )
            reading_y += line_height
        # Vertical line
        line_x = col1_x + week_w + 28
        line_top = col_baseline_y - serif_ascent_col - 6
        last_baseline = reading_y - line_height + serif_ascent_col
        line_bottom = last_baseline + 24
        vertical_line = {"rect": [line_x, line_top, line_x + 1, line_bottom]}
        return {
            "week": week_layout,
            "readings": readings_layout,
            "vertical_line": vertical_line,
            "last_baseline": last_baseline,
        }

    def wrap_text(self, text: str, font: Any, max_width: int) -> List[str]:
        """Wrap text to fit within max_width using the given font. Returns a list of lines."""
        return []
