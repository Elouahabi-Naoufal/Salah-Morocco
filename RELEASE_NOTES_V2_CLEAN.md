# Salah Times v2.0 - Release Notes

## Major New Features

### Monthly Calendar View
- Full month prayer times in calendar grid format
- Navigate between months with arrow buttons
- Today's date highlighted in green
- Weekend highlighting (Friday/Saturday)
- Export to PDF functionality
- Multi-language month names

### Weekly Schedule View
- 7-day prayer schedule (Monday to Sunday)
- Week navigation (Previous/Next week)
- Current day highlighting
- Day names in selected language
- Clean tabular layout

### Multiple Timezone View
- Compare prayer times across multiple cities
- Add/remove cities dynamically
- Display city coordinates (latitude/longitude)
- Show local time for each city
- Highlight current user's city
- Support for all 43 Moroccan cities

## Technical Improvements

### Enhanced UI/UX
- Modern gradient backgrounds
- Consistent Islamic green theme (#2d5a27)
- Responsive table layouts
- Professional dialog styling
- Improved typography and spacing

### Menu System
- New "View" menu in menu bar
- Easy access to all display features
- Menu updates with language changes
- Keyboard navigation support

### Data Management
- Improved offline data caching
- Better error handling for missing data
- Graceful fallbacks for incomplete information
- Optimized data loading performance

## Language Support

All new features support the existing 3 languages:
- English - Complete interface
- Arabic - Full Arabic support with RTL
- French - French without accents

## City Coverage

43 Moroccan Cities Supported:
- Major cities: Tangier, Casablanca, Rabat, Marrakech, Fes, Agadir
- Regional centers: Meknes, Oujda, Kenitra, Tetouan, Safi
- All other Moroccan cities with precise coordinates

## Distribution

### AppImage (Linux)
- File: SalahTimes-x86_64.AppImage
- Size: 61 MB
- Compatibility: All major Linux distributions
- Self-contained: No dependencies required

### Build Scripts
- build_appimage_updated.sh - Linux AppImage
- build_windows.bat - Windows executable
- build_android_working.sh - Android APK

## Visual Enhancements

### Calendar View
- Grid layout with proper column sizing
- Color-coded highlighting system
- Professional table headers
- Responsive design

### Weekly View
- Compact 7-day overview
- Date range display in header
- Alternating row colors
- Clear day/date formatting

### Timezone View
- Multi-city comparison table
- Coordinate display for accuracy
- Real-time local time
- Visual city highlighting

## Backward Compatibility

- All existing features preserved
- Same configuration files
- Compatible with existing data cache
- No breaking changes to core functionality

## Installation & Usage

### Linux (AppImage)
```bash
chmod +x SalahTimes-x86_64.AppImage
./SalahTimes-x86_64.AppImage
```

### Access New Features
1. Launch application
2. Click "View" in menu bar
3. Select desired view:
   - Monthly Calendar
   - Weekly Schedule
   - Multiple Timezones

## System Requirements

### Minimum Requirements
- Linux x86_64 (64-bit)
- 100 MB free disk space
- 512 MB RAM
- Internet connection (for initial data)

### Recommended
- Modern Linux distribution (Ubuntu 18.04+)
- 1 GB RAM
- Stable internet connection

## Bug Fixes

- Fixed prayer time calculation edge cases
- Improved offline mode reliability
- Better error handling for network issues
- Enhanced memory management
- Resolved UI scaling issues

## Future Roadmap

### Planned for v2.1
- Prayer completion tracking
- Custom Iqama delay settings
- Audio adhan support
- Print functionality

### Under Consideration
- Hijri calendar integration
- Prayer statistics
- Custom themes
- Widget mode

## Version Comparison

| Feature | v1.0 | v2.0 |
|---------|------|------|
| Basic Prayer Times | Yes | Yes |
| 43 Cities | Yes | Yes |
| 3 Languages | Yes | Yes |
| System Tray | Yes | Yes |
| Monthly Calendar | No | Yes |
| Weekly Schedule | No | Yes |
| Timezone Comparison | No | Yes |
| Menu System | No | Yes |
| Modern UI | No | Yes |

## Release Summary

Salah Times v2.0 represents a major evolution of the prayer times application, adding comprehensive calendar and scheduling views while maintaining the simplicity and reliability of the original. The new display features provide users with powerful tools for prayer planning and multi-city comparison, all wrapped in a modern, professional interface.

Key Highlights:
- 3 major new display features
- Enhanced UI with Islamic theming
- Professional AppImage distribution
- Full backward compatibility
- Comprehensive multi-language support

This release transforms Salah Times from a simple prayer times display into a complete Islamic calendar and scheduling application.