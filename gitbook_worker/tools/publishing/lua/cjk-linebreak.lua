-- Add LaTeX-only break opportunities after CJK characters.
--
-- Rationale:
-- The publisher uses configured luaotfload font fallbacks for glyph coverage.
-- Loading LuaTeX-ja and assigning the custom ERDA CJK font as a JFont can fail
-- with minimal fallback fonts. This filter keeps font handling unchanged and
-- only adds harmless TeX breakpoints in CJK runs.

local function is_cjk(cp)
  if cp >= 0x3400 and cp <= 0x4DBF then return true end -- CJK Extension A
  if cp >= 0x4E00 and cp <= 0x9FFF then return true end -- CJK Unified
  if cp >= 0xF900 and cp <= 0xFAFF then return true end -- Compatibility Ideographs
  if cp >= 0x3040 and cp <= 0x30FF then return true end -- Hiragana/Katakana
  if cp >= 0xAC00 and cp <= 0xD7AF then return true end -- Hangul Syllables
  if cp >= 0x3000 and cp <= 0x303F then return true end -- CJK punctuation
  if cp >= 0xFF00 and cp <= 0xFFEF then return true end -- Fullwidth forms
  return false
end

function Str(elem)
  if not FORMAT:match('latex') then
    return nil
  end

  local result = {}
  local changed = false

  for _, cp in utf8.codes(elem.text) do
    local char = utf8.char(cp)
    table.insert(result, pandoc.Str(char))
    if is_cjk(cp) then
      table.insert(result, pandoc.RawInline('latex', '\\allowbreak{}'))
      changed = true
    end
  end

  if changed then
    return result
  end
  return nil
end