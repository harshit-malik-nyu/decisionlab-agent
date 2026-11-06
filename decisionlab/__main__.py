import argparse
import json
from pathlib import Path
from .data import CASES
from .runner import LocalModel, run_model, run_baseline
from .benchmark import build

def main():
    parser=argparse.ArgumentParser(description='DecisionLab synthetic investigation lab')
    parser.add_argument('command',choices=['demo','agent','benchmark'])
    parser.add_argument('--case',choices=CASES,default='clean')
    parser.add_argument('--model',default='qwen3:4b')
    parser.add_argument('--output',default=None)
    args=parser.parse_args()
    if args.command=='benchmark':
        build(args.output or 'site/runs.json')
        print('Authored regression suite written; live model evaluation not implied.')
        return
    try:
        run=run_model(args.case,LocalModel(args.model)) if args.command=='agent' else run_baseline(args.case)
    except (OSError,ValueError,KeyError) as error:
        parser.exit(2, 'Live agent failed; no baseline substituted: '+str(error)+'\n')
    payload=json.dumps(run,indent=2)+'\n'
    if args.output:
        Path(args.output).write_text(payload)
    else:
        print(payload)
if __name__=='__main__':
    main()
