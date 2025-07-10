# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Poco is a cross-engine UI automation framework that supports Unity3D, cocos2dx, Android/iOS native apps, and other platforms. It provides a unified API for UI element selection, interaction, and testing across different game engines and applications.

## Development Commands

### Testing
- **Run tests with coverage**: `nosetests test --with-coverage --cover-package ./poco --cover-html`
- **Windows test runner**: `runtest.bat` (includes coverage report generation)
- **Test structure**: Tests are located in `test/` directory

### Installation and Setup
- **Install package**: `pip install pocoui` (published package name)
- **Install from source**: `pip install -e .` (after cloning repository)
- **Dependencies**: Listed in `requirements.txt` (six, requests, airtest, hrpc, websocket-client)

### Documentation
- **Build docs**: `cd DocBuilder && ./build.sh` (requires Sphinx)
- **Documentation source**: `DocBuilder/` contains Sphinx configuration and source files
- **Output**: Documentation is built to `doc-auto/` directory

## Architecture Overview

### Core Components

#### 1. Framework Layer (`poco/pocofw.py`)
- **Poco**: Main class providing the public API for UI automation
- Entry point for all operations: element selection, waiting, actions
- Manages configuration (timeouts, intervals, action behaviors)

#### 2. Proxy System (`poco/proxy.py`)
- **UIObjectProxy**: Represents UI elements with lazy evaluation
- Provides high-level operations: `click()`, `swipe()`, `drag_to()`, `scroll()`
- Supports hierarchical selection: `child()`, `parent()`, `sibling()`, `offspring()`
- Handles coordinate transformations and focus points

#### 3. Agent Layer (`poco/agent.py`)
- **PocoAgent**: Aggregates four main interfaces for device communication
  - **HierarchyInterface**: UI tree traversal and element selection
  - **InputInterface**: Touch, swipe, and input simulation
  - **ScreenInterface**: Screen capture and resolution management
  - **CommandInterface**: Optional arbitrary device communication

#### 4. SDK Abstraction (`poco/sdk/`)
- **AbstractDumper**: Defines UI hierarchy crawling and serialization
- **AbstractNode**: Represents UI elements with attributes and relationships
- **Selector**: Implements DFS-based element selection with complex queries
- **DefaultMatcher**: Handles attribute matching and filtering

### Platform Drivers

#### Driver Types
- **Android**: `poco/drivers/android/` - Native Android app automation via UiAutomation
- **Unity3D**: `poco/drivers/unity3d/` - Game engine automation with VR support
- **Standard**: `poco/drivers/std/` - Generic implementation for any platform supporting Poco SDK
- **Desktop**: OSX and Windows native application automation
- **Game Engines**: UE4, Cocos2d-x JavaScript support

#### Driver Architecture
Each driver implements the agent interfaces while handling platform-specific details:
- Communication protocols (TCP, WebSocket, ADB forwarding)
- Platform-specific operations (right-click, keyboard events)
- Coordinate system transformations
- Performance optimizations (frozen UI hierarchies)

### Key Utilities (`poco/utils/`)

#### Communication
- **simplerpc/**: JSON-RPC client/server for network communication
- **net/transport/**: TCP, WebSocket, HTTP transport protocols
- **hrpc/**: High-level RPC with hierarchy-specific optimizations

#### Integration
- **airtest/**: Integration with Airtest framework for device management
- **device.py**: Device abstraction and selection
- **query_util.py**: Query expression building and parsing

#### Specialized Features
- **multitouch_gesture.py**: Multi-finger gesture generation
- **track.py**: Motion track recording and playback
- **measurement.py**: Performance measurement utilities
- **vector.py**: 2D vector mathematics for coordinates

## Development Guidelines

### Code Structure
- **Layered architecture**: Clear separation between API, proxy, agent, and driver layers
- **Platform abstraction**: SDK interfaces allow adding new platforms without changing core code
- **Lazy evaluation**: UI queries are stored and executed only when needed for performance
- **Extensible design**: Easy to add new drivers for additional platforms

### Testing Approach
- Tests are located in `test/` directory
- Use `nosetests` for running tests with coverage
- Test both core framework functionality and driver-specific features
- Coverage reports are generated in `cover/` directory

### Key Concepts
- **Normalized coordinates**: Screen coordinates from 0-1 for cross-device compatibility
- **Local positioning**: Element-relative coordinates for flexible targeting
- **Frozen hierarchies**: Immutable UI snapshots for performance optimization
- **Query expressions**: Complex element selection with parent-child relationships

### Integration Points
- **Airtest compatibility**: Leverages Airtest for device management and input simulation
- **Game engine SDKs**: Requires platform-specific SDK integration in target applications
- **Network protocols**: Supports multiple transport mechanisms for different platforms
- **Cross-platform**: Designed to work with Python 2.7 and Python 3.3+