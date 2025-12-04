# Configuration-Aware Testing Guide

## Problem Statement

**BAD:** Tests that break when users change configuration
```python
def test_emoji_bad():
    pdf = build_pdf("Test 😀", emoji_color=True)
    fonts = extract_fonts(pdf)
    assert "Twemoji Mozilla" in fonts  # ❌ BREAKS if fonts.yml changes!
```

**GOOD:** Tests that adapt to current configuration
```python
def test_emoji_good(expected_emoji_font):
    pdf = build_pdf("Test 😀", emoji_color=True)
    fonts = extract_fonts(pdf)
    assert expected_emoji_font in fonts  # ✅ Reads from fonts.yml
```

## Why This Matters

**User Scenario:**
1. User downloads gitbook-worker
2. User edits `gitbook_worker/defaults/fonts.yml` to use a different emoji font instead of Twemoji Mozilla
3. User edits their `publish.yml` with custom fonts
4. User runs `pytest`
5. **❌ Tests fail with "Twemoji Mozilla not found"**

**Root Cause:** Tests have hardcoded assumptions about which fonts are configured.

**Solution:** Tests MUST derive expectations from actual configuration files.

## Available Fixtures

### `default_font_config` (session scope)
Loads the actual `gitbook_worker/defaults/fonts.yml` from the codebase.
Use for integration tests that should validate against production configuration.

```python
def test_with_default_config(default_font_config):
    """This test uses the ACTUAL fonts.yml configuration."""
    emoji_font = default_font_config.get_font("EMOJI")
    assert emoji_font is not None
    assert emoji_font.name != ""
```

### `test_font_config` (function scope)
Creates an isolated, temporary `fonts.yml` for unit tests.
Each test gets its own configuration that won't affect other tests.

```python
def test_with_isolated_config(test_font_config):
    """This test has its own fonts.yml that can be modified."""
    test_emoji = test_font_config.get_font("TEST_EMOJI")
    assert test_emoji.name == "DejaVu Sans"  # From fixture definition
```

### `expected_emoji_font` (function scope)
Returns the configured emoji font name from `fonts.yml`.
This is what tests should use instead of hardcoding "Twemoji Mozilla".

```python
def test_pdf_uses_configured_emoji(tmp_path, expected_emoji_font):
    """Test that PDF uses whatever emoji font is configured."""
    pdf = generate_pdf(tmp_path, content="Test 😀")
    fonts = extract_fonts(pdf)
    
    # ✅ CORRECT: Uses dynamic expectation
    assert expected_emoji_font in fonts, (
        f"Expected emoji font '{expected_emoji_font}' not found. "
        f"Available fonts: {fonts}"
    )
```

### `expected_main_fonts` (function scope)
Returns configured main fonts (serif, sans, mono) as a dict.

```python
def test_main_fonts(tmp_path, expected_main_fonts):
    """Test uses configured serif/sans/mono fonts."""
    pdf = generate_pdf(
        tmp_path,
        main_font=expected_main_fonts["serif"],
        sans_font=expected_main_fonts["sans"],
    )
    # ... validate PDF ...
```

### `test_publish_config` (function scope)
Returns a complete `publish.yml` configuration dict that's valid according to current `fonts.yml`.

```python
def test_full_pipeline(tmp_path, test_publish_config):
    """Test complete pipeline with valid configuration."""
    # Config is already populated with fonts from fonts.yml
    config = test_publish_config
    assert config["pdf_options"]["emoji_color"] == True
    assert config["pdf_options"]["main_font"] in ["DejaVu Serif", ...]
```

## Writing New Tests

### DO: Test Behavior, Not Configuration
```python
# ✅ GOOD: Tests the BEHAVIOR
def test_emoji_color_setting_works(tmp_path, expected_emoji_font):
    """When emoji_color=true, PDF should contain configured emoji font."""
    pdf = build_with_emoji_color(tmp_path, emoji_color=True)
    assert expected_emoji_font in extract_fonts(pdf)

# ❌ BAD: Tests specific configuration value
def test_uses_twitter_emoji(tmp_path):
    """PDF should use Twemoji Mozilla."""  # Assumes specific font!
    pdf = build_with_emoji_color(tmp_path, emoji_color=True)
    assert "Twemoji Mozilla" in extract_fonts(pdf)
```

### DO: Use Fixtures for Expectations
```python
# ✅ GOOD: Fixture provides expectation
def test_with_fixture(expected_emoji_font):
    assert validate_emoji_font(expected_emoji_font)

# ❌ BAD: Hardcoded expectation
def test_without_fixture():
    assert validate_emoji_font("Twemoji Mozilla")
```

### DO: Provide Clear Failure Messages
```python
# ✅ GOOD: Helpful error message
def test_with_context(expected_emoji_font):
    fonts = get_pdf_fonts()
    assert expected_emoji_font in fonts, (
        f"Expected '{expected_emoji_font}' from fonts.yml configuration, "
        f"but PDF contains: {fonts}. "
        f"Check that fonts.yml EMOJI entry matches publish.yml settings."
    )

# ❌ BAD: Cryptic error
def test_without_context(expected_emoji_font):
    assert expected_emoji_font in get_pdf_fonts()
```

### DO: Skip When Configuration Unavailable
```python
# ✅ GOOD: Graceful skip
def test_requires_emoji_font(default_font_config):
    emoji = default_font_config.get_font("EMOJI")
    if not emoji:
        pytest.skip("No EMOJI font configured in fonts.yml")
    
    # Test proceeds with emoji configuration...

# ❌ BAD: Assumes configuration exists
def test_assumes_emoji():
    emoji = load_emoji_font()  # May return None!
    assert emoji.name == "..."  # AttributeError!
```

## Testing Custom Configurations

### Scenario: Test with Alternative Emoji Font
```python
def test_alternative_emoji_font(tmp_path):
    """Test that system works with alternative emoji font configuration."""
    
    # Create custom fonts.yml with alternative emoji font
    custom_fonts = tmp_path / "fonts.yml"
    custom_fonts.write_text("""
version: 1.0.0
fonts:
  EMOJI:
    name: "Segoe UI Emoji"
    paths:
      - "C:/Windows/Fonts/seguiemj.ttf"
    license: "Microsoft EULA"
    license_url: "https://www.microsoft.com/"
    version: "1.00"
""")
    
    # Load custom configuration
    from gitbook_worker.tools.publishing.font_config import FontConfigLoader
    config = FontConfigLoader(config_path=custom_fonts)
    
    # Test with this configuration
    emoji_font = config.get_font("EMOJI")
    assert emoji_font.name == "Segoe UI Emoji"
    
    # Generate PDF using this config
    # ... rest of test ...
```

### Scenario: Test Font Fallback Chain
```python
def test_fallback_chain(default_font_config):
    """Test that font fallback respects configured fonts."""
    
    # Get configured fallback fonts
    cjk_font = default_font_config.get_font("CJK")
    emoji_font = default_font_config.get_font("EMOJI")
    
    # Build fallback string as pipeline would
    fallback = f"{emoji_font.name}:mode=harf; {cjk_font.name}:mode=harf"
    
    # Test PDF generation with this fallback
    pdf = build_pdf_with_fallback(fallback)
    fonts = extract_fonts(pdf)
    
    # Verify both fallback fonts are present
    assert emoji_font.name in fonts
    assert cjk_font.name in fonts
```

## Common Pitfalls

### ❌ Pitfall 1: Assuming System Fonts
```python
# BAD: Assumes font is installed on system
def test_system_font():
    pdf = build_pdf(main_font="Arial")  # May not exist!
    assert "Arial" in extract_fonts(pdf)
```

**Fix:** Only test with fonts from `fonts.yml`:
```python
def test_configured_font(expected_main_fonts):
    pdf = build_pdf(main_font=expected_main_fonts["serif"])
    assert expected_main_fonts["serif"] in extract_fonts(pdf)
```

### ❌ Pitfall 2: Path Assumptions
```python
# BAD: Hardcoded paths
def test_font_file():
    assert Path("/usr/share/fonts/emoji.ttf").exists()
```

**Fix:** Use FontConfig to resolve paths:
```python
def test_font_available(default_font_config):
    emoji = default_font_config.get_font("EMOJI")
    assert len(emoji.paths) > 0
    # Note: Path may not exist yet if font needs download
```

### ❌ Pitfall 3: Version Coupling
```python
# BAD: Tests specific version
def test_emoji_version():
    assert get_emoji_version() == "15.1.0"
```

**Fix:** Test that version is specified:
```python
def test_emoji_has_version(default_font_config):
    emoji = default_font_config.get_font("EMOJI")
    assert emoji.version is not None
    assert emoji.version != ""
```

## Testing Philosophy

**Goal:** Tests should validate that the SYSTEM WORKS with CONFIGURED fonts.

**Not Goal:** Tests should not validate that SPECIFIC fonts are configured.

**Example:**
- ✅ "emoji_color=true produces colored emojis using the configured emoji font"
- ❌ "emoji_color=true produces colored emojis using Twemoji Mozilla v15.1.0"

## Related Documentation

- Main concept: `gitbook_worker/docs/backlog/publish-yml-comprehensive-testing.md`
- Font configuration: `gitbook_worker/defaults/fonts.yml`
- Font config loader: `gitbook_worker/tools/publishing/font_config.py`
- AGENTS.md sections 12-14: Font management principles

## Quick Reference

```python
# Good pattern for font-related tests:
@pytest.mark.integration
def test_pdf_font_feature(
    tmp_path,
    expected_emoji_font,      # From fonts.yml
    expected_main_fonts,      # From fonts.yml
    test_publish_config,      # Valid config matching fonts.yml
):
    """Test feature X with configured fonts."""
    
    # Use fixtures for all font expectations
    config = test_publish_config
    
    # Generate PDF
    pdf = build_pdf(tmp_path, config)
    
    # Validate against fixtures
    fonts = extract_fonts(pdf)
    assert expected_emoji_font in fonts
    assert expected_main_fonts["serif"] in fonts
```

---

**Remember:** When in doubt, ask: "Will this test still pass if a user changes fonts.yml?"
If answer is no → use fixtures! ✅
