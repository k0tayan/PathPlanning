python retrain.py \
  --bottleneck_dir=bottlenecks \
  --how_many_training_steps=100 \
  --model_dir=inception \
  --summaries_dir=training_summaries/basic \
  --output_graph=retrained_graph_green_up.pb \
  --output_labels=retrained_labels_up.txt \
  --image_dir=up