########## Train from scratch ##########
# Step 1: leading plus event bart
python3 tasks/event-trigger/train.py --data_dir=datasets/event-trigger/limerick\
 --learning_rate=8e-5 --train_batch_size=16 --eval_batch_size=10 --model_name_or_path=facebook/bart-base \
 --output_dir=output/limericks --model_name leading-plus-event-bart --experiment_name=leading-plus-event-bart-limericks\
 --val_check_interval=1.0 --limit_val_batches=10 --max_epochs=3 --accum_batches_args=4  --num_sanity_val_steps=0
 
 # Step 2: event lm
 python3 tasks/event-trigger/train.py --data_dir=datasets/event-trigger/limerick\
 --learning_rate=1e-4 --train_batch_size=16 --eval_batch_size=10 --model_name_or_path=output/limericks/leading-plus-event-bart-limericks/best_tfmr \
 --output_dir=output/limericks --model_name event-lm --experiment_name=event-lm-limericks\
 --val_check_interval=1.0 --limit_val_batches=10 --max_epochs=3 --accum_batches_args=4  --num_sanity_val_steps=0
 
 # Step 3: event lm sbert
 python3 tasks/event-trigger/train.py --data_dir=datasets/event-trigger/limerick\
 --learning_rate=1e-4 --train_batch_size=16 --eval_batch_size=10 --model_name_or_path=output/limericks/event-lm-limericks/best_tfmr \
 --output_dir=output/limericks --model_name event-lm-sbert --experiment_name=event-lm-sbert-limericks\
 --val_check_interval=1.0 --limit_val_batches=10 --max_epochs=3 --accum_batches_args=4  --num_sanity_val_steps=0
 
 
 ########## Train with ckpt ##########
 # Download the ckpt from GitHub and put it in path output/event-trigger/
 python3 tasks/event-trigger/train.py --data_dir=datasets/event-trigger/limerick\
 --learning_rate=1e-4 --train_batch_size=16 --eval_batch_size=10 --model_name_or_path=output/event-trigger/event-lm-sbert-roc-stories/best_tfmr \
 --output_dir=output/limericks --model_name event-lm-sbert --experiment_name=event-lm-sbert-limericks\
 --val_check_interval=1.0 --limit_val_batches=10 --max_epochs=3 --accum_batches_args=4  --num_sanity_val_steps=0
 
 
 ########## Test ##########
 python3 tasks/event-trigger/test.py --data_dir=datasets/event-trigger/limerick\
  --eval_batch_size=10 --model_name_or_path=output/limericks/event-lm-sbert-limericks/best_tfmr \
  --output_dir=output/limericks --model_name event-lm-sbert --experiment_name=event-lm-sbert-limericks\
  --test_event_infix=_event --limerick_sep_token="."
