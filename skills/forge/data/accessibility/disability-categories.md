<!-- gdd-forge knowledge base · scavenged from BMad GDD Generator (MIT) · reference only: agents may cite facts from this file; nothing else counts as an external source -->
# Accessibility Standards — Disability Categories and Considerations

## Disability Categories and Considerations

### Visual Disabilities

#### Blindness
**Population**: ~1% of global population
**Assistive Technologies**: Screen readers, braille displays, voice control
**Design Considerations**:
- Complete screen reader compatibility
- Audio descriptions for visual elements
- Spatial audio for navigation
- Haptic feedback for interactions
- Voice-based input alternatives

**Implementation Requirements**:
- Semantic markup and labels
- Focus management and navigation
- Audio cues for all visual feedback
- Keyboard-only operation
- Clear audio descriptions

#### Low Vision
**Population**: ~3-4% of global population
**Assistive Technologies**: Screen magnifiers, high contrast displays
**Design Considerations**:
- Scalable text and UI elements
- High contrast color schemes
- Customizable visual settings
- Clear visual hierarchy
- Reduced visual clutter

**Implementation Requirements**:
- Minimum 4.5:1 color contrast
- Scalable fonts and UI elements
- Customizable color schemes
- Clear focus indicators
- Consistent visual patterns

#### Color Blindness
**Population**: ~8% of men, ~0.5% of women
**Types**: Protanopia, Deuteranopia, Tritanopia, Monochromacy
**Design Considerations**:
- Color-independent information design
- Pattern and texture alternatives
- Colorblind-friendly palettes
- Customizable color options
- Clear visual distinctions

**Implementation Requirements**:
- Never rely solely on color for information
- Provide pattern/texture alternatives
- Test with colorblind simulation tools
- Offer colorblind-friendly themes
- Use sufficient contrast ratios

### Hearing Disabilities

#### Deafness
**Population**: ~0.1-0.2% of global population
**Communication**: Sign language, written text, visual cues
**Design Considerations**:
- Complete visual alternatives to audio
- Sign language interpretation (where applicable)
- Visual sound indicators
- Haptic feedback alternatives
- Text-based communication

**Implementation Requirements**:
- Comprehensive subtitles/captions
- Visual sound effect indicators
- Haptic feedback for audio cues
- Text chat alternatives
- Visual notification systems

#### Hard of Hearing
**Population**: ~15% of global population
**Assistive Technologies**: Hearing aids, cochlear implants, amplifiers
**Design Considerations**:
- Adjustable audio settings
- Visual audio indicators
- Clear audio quality
- Frequency customization
- Volume control options

**Implementation Requirements**:
- Customizable audio settings
- Visual audio cues
- Clear, high-quality audio
- Subtitle/caption options
- Audio description alternatives

### Motor Disabilities

#### Limited Fine Motor Control
**Population**: ~2-3% of global population
**Assistive Technologies**: Adaptive controllers, switch devices, eye tracking
**Design Considerations**:
- Large touch targets (minimum 44px)
- Adjustable timing requirements
- Alternative input methods
- Gesture simplification
- Error prevention and correction

**Implementation Requirements**:
- Minimum touch target sizes
- Adjustable time limits
- Alternative input support
- Gesture customization
- Undo/redo functionality

#### Limited Mobility
**Population**: ~1-2% of global population
**Assistive Technologies**: One-handed controllers, foot switches, head tracking
**Design Considerations**:
- One-handed operation options
- Reduced physical requirements
- Alternative control schemes
- Customizable input mapping
- Assistive device support

**Implementation Requirements**:
- Single-handed operation modes
- Button remapping capabilities
- Alternative control schemes
- External device support
- Reduced physical demands

### Cognitive Disabilities

#### Learning Disabilities
**Population**: ~10-15% of global population
**Types**: Dyslexia, ADHD, autism spectrum disorders
**Design Considerations**:
- Clear, simple language
- Consistent navigation patterns
- Reduced cognitive load
- Multiple learning modalities
- Customizable complexity

**Implementation Requirements**:
- Plain language usage
- Consistent UI patterns
- Simplified mode options
- Multi-modal information presentation
- Customizable difficulty settings

#### Memory Impairments
**Population**: ~5-10% of global population (including age-related)
**Design Considerations**:
- Clear progress indicators
- Frequent save opportunities
- Context reminders
- Simplified navigation
- Consistent patterns

**Implementation Requirements**:
- Auto-save functionality
- Progress tracking displays
- Context-sensitive help
- Breadcrumb navigation
- Consistent interaction patterns

