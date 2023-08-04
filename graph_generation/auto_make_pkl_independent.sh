echo "Removing previous data"
rm ../main_data_folder/data/ortho_{train,test,valid}_dataset_folder_preprocess/*
rm step1/* step2/* step3/*
./make_graphs 10 30 1000 150 1 step1

realpath step1/* > input.txt
cat input.txt | xargs -I % bash generate_graph.sh %
python json_to_pkl.py
cp step3/output_graphn10e30s150i{0..799}planar.pkl ../main_data_folder/data/ortho_train_dataset_folder_preprocess 
cp step3/output_graphn10e30s150i{800..899}planar.pkl ../main_data_folder/data/ortho_test_dataset_folder_preprocess 
cp step3/output_graphn10e30s150i{900..999}planar.pkl ../main_data_folder/data/ortho_valid_dataset_folder_preprocess 


