input=$1
output_dir=step2

filename=$(basename $input)
name=${filename%.*}
echo "Generate graph for $filename"

# execute binary
./ortho step1/${filename}

# post process
# remove the first line of gml output
echo "$(tail -n +2 output_${name}.gml)" > output_${name}.gml
# generate json file
python post_process.py output_${name}.gml

# file organization and cleanup
# mv output_${name}.gml   $output_dir/
mv output_${name}.json  $output_dir/
# mv output_${name}.svg   $output_dir/
rm output_${name}.svg
rm output_${name}.gml
# rm ${name}.dot ${name}.gml ${name}.csv

