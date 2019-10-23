# -*- coding: utf-8 -*-
import re

from pynlple.utils import itemgetter

__rn_patt = re.compile(r'(\r|\n|&#10;|&#13;)+')
__b_patt = re.compile(r'</?b>')


def __find_local_index(parts, abs_index):
    cur_index = 0
    for i, part in enumerate(parts):
        part_len = len(part)
        upd_index = cur_index + part_len
        if upd_index > abs_index:
            return i, abs_index - cur_index
        cur_index = upd_index
    return len(parts), 0


def __cut_pos_analysis_title(mystem_pos_analysis):
    analysis = list(mystem_pos_analysis)
    rec_parts = list(map(itemgetter('text', ''), analysis))
    rec_text = ''.join(rec_parts)
    first_rn_match = __rn_patt.search(rec_text)
    if first_rn_match:
        part_cut_index, local_cut_index = __find_local_index(rec_parts, first_rn_match.start())
        updated_nodes = analysis[:part_cut_index + 1]
        updated_node = dict(updated_nodes[part_cut_index])
        updated_node['text'] = updated_node.get('text', '')[:local_cut_index]
        updated_nodes[part_cut_index] = updated_node
        return updated_nodes
    return analysis


def __cut_pos_analysis_description(mystem_pos_analysis):
    analysis = list(mystem_pos_analysis)
    rec_parts = list(map(itemgetter('text', ''), analysis))
    rec_text = ''.join(rec_parts)
    first_rn_match = __rn_patt.search(rec_text)
    if first_rn_match:
        part_cut_index, local_cut_index = __find_local_index(rec_parts, first_rn_match.end())
        updated_nodes = analysis[part_cut_index:]
        updated_node = dict(updated_nodes[0])
        updated_node['text'] = updated_node.get('text', '')[local_cut_index:]
        updated_nodes[0] = updated_node
        return updated_nodes
    return analysis


def cut_title_or_description(youtube_post_highlighted_text, pos_analysis):
    first_rn_match = __rn_patt.search(youtube_post_highlighted_text)
    if first_rn_match:
        b_matches = list(__b_patt.finditer(youtube_post_highlighted_text))
        if len(b_matches) > 0:
            f_b = b_matches[0]
            l_b = b_matches[-1]
            has_b_in_title = f_b.end() < first_rn_match.start()
            has_b_in_description = l_b.start() > first_rn_match.end()
            if has_b_in_title and not has_b_in_description:
                return youtube_post_highlighted_text[:first_rn_match.start()], __cut_pos_analysis_title(pos_analysis)
            elif has_b_in_description and not has_b_in_title:
                return youtube_post_highlighted_text[first_rn_match.end():], __cut_pos_analysis_description(pos_analysis)
    return youtube_post_highlighted_text, pos_analysis


def cut_text_with_highlights_if_present(youtube_post_raw_text, highlights):
    if len(highlights) > 0:
        first_rn_match = __rn_patt.search(youtube_post_raw_text)
        if first_rn_match:
            f_b = min(map(itemgetter('start'), highlights))
            l_b = max(map(itemgetter('end'), highlights))
            has_b_in_title = f_b < first_rn_match.start()
            has_b_in_description = l_b > first_rn_match.end()
            if has_b_in_title and not has_b_in_description:
                return youtube_post_raw_text[:first_rn_match.start()], __cut_highlights(highlights, first_rn_match.start(), first_rn_match.end())[0]
            elif has_b_in_description and not has_b_in_title:
                return youtube_post_raw_text[first_rn_match.end():], __cut_highlights(highlights, first_rn_match.start(), first_rn_match.end())[1]
    return youtube_post_raw_text, highlights


def __cut_highlights(highlights, cut_start, cut_end):
    l_highlights = []
    r_highlights = []

    for highlight in highlights:
        s = highlight['start']
        e = highlight['end']
        if s < cut_start and e <= cut_start:
            l_highlights.append(highlight)
        elif s > cut_end and e > cut_end:
            r_highlights.append(highlight)
        elif s < cut_start and e > cut_end:
            l_highlights.append({'start': s, 'end': cut_start})
            r_highlights.append({'start': cut_end, 'end': e})
        elif cut_start <= s <= cut_end and e > cut_end:
            r_highlights.append({'start': cut_end, 'end': e})
        elif s < cut_start and cut_start < e <= cut_end:
            l_highlights.append({'start': s, 'end': cut_start})

    return l_highlights, r_highlights
