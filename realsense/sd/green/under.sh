python retrain.py \
  --bottleneck_dir=bottlenecks \
  --how_many_training_steps=100 \
  --model_dir=inception \
  --summaries_dir=training_summaries/basic \
  --output_graph=retrained_graph_green_under.pb \
  --output_labels=retrained_labels_under.txt \
  --image_dir=under