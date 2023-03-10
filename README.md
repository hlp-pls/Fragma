# Fragma
[WEBSITE UNDERCONSTRUCTION](https://hlp-pls.github.io/Fragma/) <br>
GLSL editor for playing with fragment shader. <br>
Multipass rendering with various buffer sizes and iterations. <br>
Currently only supports MacOS versions same or higher than 12.0.1 (bulit on 12.0.1) <br>
No support yet for Windows and Linux. <br>

## Dependencies
Built using [fbs](https://build-system.fman.io/)
[dependencies](https://github.com/hlp-pls/Fragma/blob/master/requirements/base.text)

## How To Use
[latest release](https://github.com/hlp-pls/Fragma/releases/latest) <br>
[examples folder](https://github.com/hlp-pls/Fragma/tree/master/examples) <br>


Fragma v0.0.5

- Install with .dmg file
- Open Fragma
- Set window size and preferred frame-rate
- Edit GLSL code and click play button / stop with stop button
- Open files (shortcut: command + o) with .fragma extension included in examples folder
- Save files (shortcut: command + s) (save with the last pass editor selected to prevent pass order mixup)
- Add passes with "+" button (5 passes max)
- Each pass has two number inputs "compression" and "iteration". 
- Compression lower than 1.0 makes the pass smaller than the window buffer. 
- Iteration sets the number of times the pass should be rendered each animation frame.
- Add each pass as texture uniform (you can only add from a different pass - to reference the current pass texture, use bckbuffer uniform instead) by clicking buttons below editor.
- Use capture button when the project is running. It will capture a frame and close.
- Use recording to record as video.

*** no GLSL version change available


## Usage Example
[video recording (realtime)](https://youtu.be/dSDGOPqqVj8)


## Copyright
Made by [Choi gunhyuk](https://www.instagram.com/ch_gnhk/)


Copyright 2023 Choi Gunhyuk

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

