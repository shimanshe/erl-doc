# erl-doc
create erlang chm manual file.

### Requirement
you must install [python 3.x](https://www.python.org/downloads/) first.

### How to use
git clone https://github.com/shimanshe/erl-doc.git
cd erl-doc
python3 main.py

there are 4 options to select,
1.build_htmlhelp_prj
2.fetch_doc_html
3.handle_html
4.make_htmlhelp_prj

* 1.select 2.fetch_doc_html to download erlang man pages from erlang website.
you can run this option multiple until there is no more html file downloaded.

* 2.select handle_html to deal with the downloaded html files, such remove left navigate memu, remove javascripts.

* 3.select make_htmlhelp_prj to create chm project files, hhc, hhp, hhk.
* 4.select build_htmlhelp_prj to build html workshop project to creating chm help file.