cd docs
make html
cd ..
rm -rf oldway/docs
mv docs/_build/html oldway/docs
