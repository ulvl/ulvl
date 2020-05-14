@ECHO OFF

pushd %~dp0

REM Command file for Sphinx documentation
REM
REM Permission is hereby granted, free of charge, to any person obtaining
REM a copy of this software and associated documentation files (the
REM "Software"), to deal in the Software without restriction, including
REM without limitation the rights to use, copy, modify, merge, publish,
REM distribute, sublicense, and/or sell copies of the Software, and to
REM permit persons to whom the Software is furnished to do so, subject to
REM the following conditions:
REM
REM The above copyright notice and this permission notice shall be included
REM in all copies or substantial portions of the Software.
REM
REM THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
REM EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
REM MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
REM IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
REM CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
REM TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
REM SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

if "%SPHINXBUILD%" == "" (
	set SPHINXBUILD=sphinx-build
)
set SOURCEDIR=.
set BUILDDIR=../doc

if "%1" == "" goto help

%SPHINXBUILD% >NUL 2>NUL
if errorlevel 9009 (
	echo.
	echo.The 'sphinx-build' command was not found. Make sure you have Sphinx
	echo.installed, then set the SPHINXBUILD environment variable to point
	echo.to the full path of the 'sphinx-build' executable. Alternatively you
	echo.may add the Sphinx directory to PATH.
	echo.
	echo.If you don't have Sphinx installed, grab it from
	echo.http://sphinx-doc.org/
	exit /b 1
)

%SPHINXBUILD% -M %1 %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%
goto end

:help
%SPHINXBUILD% -M help %SOURCEDIR% %BUILDDIR% %SPHINXOPTS%

:end
popd
