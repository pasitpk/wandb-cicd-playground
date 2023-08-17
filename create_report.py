import os
import wandb
import wandb.apis.reports as wr
import argparse

if __name__ == "__main__":

    assert os.getenv('WANDB_API_KEY'), 'You must set the WANDB_API_KEY environment variable'

    parser = argparse.ArgumentParser(description="Generate a report for the comparison between a specific run and a baseline")
    parser.add_argument("--entity", type=str, help="W&B's entity")
    parser.add_argument("--project", type=str, help="Project name")
    parser.add_argument("--run_id", type=str, help="ID for the current run")
    parser.add_argument("--baseline_tag", type=str, default="baseline", help="Tag of the baseline")

    args = parser.parse_args()

    ENTITY = args['entity']
    PROJECT = args['project']
    RUN_ID = args['run_id']
    BASELINE_TAG = args['baseline_tag']

    project_path = f'{ENTITY}/{PROJECT}'
    run_path = f'{project_path}/{RUN_ID}'

    api = wandb.Api()

    tags = [BASELINE_TAG]
    baseline_runs = api.runs(project_path, 
                        {"tags": {"$in": tags}})
    
    baseline_run_names = [r.name for r in baseline_runs]

    cur_run = api.run(run_path)
    cur_run_name = cur_run.name

    all_run_names = baseline_run_names + [cur_run_name]

    report = wr.Report(
        entity=ENTITY,
        project=PROJECT,
        title='Compare Runs',
        description="A demo of comparing runs programatically"
    )  

    pg = wr.PanelGrid(
            runsets=[
                wr.Runset(ENTITY, PROJECT, "Run Comparison").set_filters_with_python_expr(f"Name in {all_run_names}")
            ],
            panels=[
                wr.RunComparer(diff_only='split', layout={'w': 24, 'h': 15}),
            ]
        )

    report.blocks = report.blocks[:1] + [pg] + report.blocks[1:]
    report.save()

    with open(os.environ['GITHUB_OUTPUT'], 'a') as f:
        print(f'WANDB_REPORT_URL={report.url}', file=f)
