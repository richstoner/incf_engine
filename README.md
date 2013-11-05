incf engine
===========

Refactor of flask skeleton, virtuoso &amp; tornado application framework


## Architecture

#### Frontend (192.168.100.10)

Manages login, job queuing, job status monitoring, and visualization



#### Engine (192.168.100.20)

Provides jobs api, runs jobs, provides local hosting service



#### VirtuosoDB (192.168.100.30)

Provides graphdb



## Launch

**Launching virtuso vm:**

    vagrant up virtuoso

Then follow directions in virtuoso/virtuoso_install.md


**Launching the processing engine:**

    vagrant up engine


Then follow directions TBD (Satra)


**Launching the frontend:**

    vagrant up frontend

    fab vagrant sysinfo

    fab vagrant base

    fab vagrant externals

    fab vagrant


















LICENSE
---------

The MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
