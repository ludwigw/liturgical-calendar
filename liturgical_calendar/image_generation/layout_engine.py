from typing import List, Tuple, Dict, Any

class LayoutEngine:
    """
    Responsible for calculating layout positions and text for each section of the liturgical image.
    Does not draw to an image; returns layout data for use by an image builder.
    """
    def create_header_layout(self, season: str, date: str, fonts: Dict[str, Any], draw: Any, width: int, padding: int) -> Dict[str, Any]:
        """Return layout info for the header row (season, dash, date)."""
        # Fonts expected: {'sans_uc': ..., 'serif': ...}
        season_text = season.upper()
        header_dash = ' — '
        date_text = date
        sans_font_36_uc = fonts['sans_uc']
        serif_font_36 = fonts['serif']
        # Measure for baseline alignment
        season_w, season_h = draw.textbbox((0, 0), season_text, font=sans_font_36_uc)[2:4]
        dash_w, dash_h = draw.textbbox((0, 0), header_dash, font=sans_font_36_uc)[2:4]
        date_w, date_h = draw.textbbox((0, 0), date_text, font=serif_font_36)[2:4]
        total_w = season_w + dash_w + date_w
        x = (width - total_w) // 2
        y = padding
        # Baseline alignment: get font metrics
        sans_ascent, sans_descent = sans_font_36_uc.getmetrics()
        serif_ascent, serif_descent = serif_font_36.getmetrics()
        baseline_y = y + max(sans_ascent, serif_ascent)
        return {
            'season': {
                'text': season_text,
                'font': sans_font_36_uc,
                'pos': (x, baseline_y - sans_ascent),
            },
            'dash': {
                'text': header_dash,
                'font': sans_font_36_uc,
                'pos': (x + season_w, baseline_y - sans_ascent),
            },
            'date': {
                'text': date_text,
                'font': serif_font_36,
                'pos': (x + season_w + dash_w, baseline_y - serif_ascent),
            },
            'baseline_y': baseline_y,
            'height': max(season_h, dash_h, date_h),
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
    ) -> Dict[str, Any]:
        """
        Return layout info for the artwork and (optionally) next artwork thumbnail and its text.
        """
        art_x = (width - art_size) // 2
        layout = {
            'main': {
                'pos': (art_x, y),
                'size': (art_size, art_size),
                'artwork': artwork,
            },
            'show_next': False,
        }
        if next_artwork and fonts and draw:
            thumb_size = art_size // 2
            thumb_x = art_x + (art_size - thumb_size) // 2
            thumb_y = y + (art_size - thumb_size) // 2
            layout['next'] = {
                'pos': (thumb_x, thumb_y),
                'size': (thumb_size, thumb_size),
                'artwork': next_artwork,
            }
            # Add next artwork label/title/date layout
            layout.update(self._create_next_artwork_layout(
                next_artwork, art_x, art_size, thumb_y, thumb_size, fonts, next_title_y_offset, draw
            ))
            layout['show_next'] = True
        return layout

    def _get_text_width(self, draw, text, font):
        bbox = draw.textbbox((0, 0), text, font=font)
        return bbox[2] - bbox[0]

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
    ) -> Dict[str, Any]:
        """
        Return layout info for the 'NEXT:' label, next artwork title, and date below the thumbnail.
        """
        next_prefix = 'NEXT: '
        next_title = next_artwork.get('name', '')
        sans_font = fonts['sans']
        serif_font = fonts['serif']
        # Baseline alignment
        sans_ascent, _ = sans_font.getmetrics()
        serif_ascent, _ = serif_font.getmetrics()
        next_prefix_w = self._get_text_width(draw, next_prefix, sans_font)
        next_title_w = self._get_text_width(draw, next_title, serif_font)
        total_next_w = next_prefix_w + next_title_w
        next_x = art_x + (art_size - total_next_w) // 2
        next_title_y = thumb_y + thumb_size + next_title_y_offset
        baseline_y = next_title_y + max(sans_ascent, serif_ascent)
        layout = {
            'next_label': {
                'text': next_prefix,
                'font': sans_font,
                'pos': (next_x, baseline_y - sans_ascent),
            },
            'next_title': {
                'text': next_title,
                'font': serif_font,
                'pos': (next_x + next_prefix_w, baseline_y - serif_ascent),
            },
        }
        # Date below the next artwork title
        next_artwork_date = next_artwork.get('date').upper()
        if next_artwork_date:
            date_text = next_artwork_date
            sans_font_26 = fonts.get('sans_26', fonts.get('sans_32', sans_font))
            date_x = next_x + next_prefix_w
            date_y = baseline_y + 8  # 8px below the title
            layout['next_date'] = {
                'text': date_text,
                'font': sans_font_26,
                'pos': (date_x, date_y),
            }
        return layout

    def create_title_layout(self, title: str, fonts: Dict[str, Any], draw: Any, width: int, padding: int, title_font_size: int, title_line_height: float, start_y: int) -> Dict[str, Any]:
        """Return layout info for the artwork title, including wrapped lines and positions."""
        font = fonts['serif_96']
        max_width = width - 2 * padding
        # Wrap text
        def wrap_text(text, font, max_width):
            words = text.split()
            lines = []
            current = ''
            for word in words:
                test = current + (' ' if current else '') + word
                w = self._get_text_width(draw, test, font)
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
            line_w = self._get_text_width(draw, line, font)
            line_x = (width - line_w) // 2
            line_y = start_y + i * int(title_font_size * title_line_height)
            layout_lines.append({'text': line, 'font': font, 'pos': (line_x, line_y)})
            last_baseline = line_y + font.getmetrics()[0]  # baseline = y + ascent
        return {'lines': layout_lines, 'last_baseline': last_baseline}

    def create_readings_layout(self, week: str, readings: list, fonts: Dict[str, Any], draw: Any, width: int, padding: int, start_y: int, line_height: int) -> Dict[str, Any]:
        """Return layout info for the week and readings columns, including vertical line and last baseline y."""
        sans_uc = fonts['sans_uc']
        serif = fonts['serif']
        # Calculate widths
        week_w = self._get_text_width(draw, week, sans_uc)
        readings_w = 0
        for r in readings:
            w = self._get_text_width(draw, r, serif)
            readings_w = max(readings_w, w)
        col_gap = 28 * 2 + 1  # 28px padding each side + 1px line
        total_cols_w = week_w + col_gap + readings_w
        col1_x = (width - total_cols_w) // 2
        col2_x = col1_x + week_w + col_gap
        # Baseline alignment
        sans_ascent_col, _ = sans_uc.getmetrics()
        serif_ascent_col, _ = serif.getmetrics()
        col_baseline_y = start_y + max(sans_ascent_col, serif_ascent_col)
        # Layout for week
        week_layout = {'text': week, 'font': sans_uc, 'pos': (col1_x, col_baseline_y - sans_ascent_col)}
        # Layout for readings
        readings_layout = []
        reading_y = col_baseline_y - serif_ascent_col
        for r in readings:
            readings_layout.append({'text': r, 'font': serif, 'pos': (col2_x, reading_y)})
            reading_y += line_height
        # Vertical line
        line_x = col1_x + week_w + 28
        cap_height = serif_ascent_col
        line_top = col_baseline_y - serif_ascent_col - 6
        last_baseline = reading_y - line_height + serif_ascent_col
        line_bottom = last_baseline + 24
        vertical_line = {'rect': [line_x, line_top, line_x + 1, line_bottom]}
        return {
            'week': week_layout,
            'readings': readings_layout,
            'vertical_line': vertical_line,
            'last_baseline': last_baseline
        }

    def wrap_text(self, text: str, font: Any, max_width: int) -> List[str]:
        """Wrap text to fit within max_width using the given font. Returns a list of lines."""
        return [] 