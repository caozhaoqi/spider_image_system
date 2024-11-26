"""
Time:     2024/1/1 00:00
Author:   ZhaoQi Cao(czq)
Version:  V 0.1
File:     log_analyis.py
Describe: Github link: https://github.com/caozhaoqi
"""

import os
import re
import sys
from pathlib import Path
from collections import Counter
from typing import List, Tuple, Dict
from loguru import logger

sys.path.append(str(Path(__file__).parent.parent))

# Error patterns
ERROR_PATTERNS = {
    'connection_broken': {
        'pattern': r'ERROR.*unknown error.*Connection broken: IncompleteRead',
        'detail': r'detail: \((.*? bytes read, .*? more expected)\)'
    },
    'remote_disconnected': {
        'pattern': r'ERROR.*unknown error.*Connection aborted\. RemoteDisconnected', 
        'detail': r'detail: \(Remote end closed connection without response\)'
    },
    'not_found': {
        'pattern': r'ERROR.*Failed to download image from',
        'detail': r'detail: <!DOCTYPE html>\n<html>\n\s*<h1>404 Not Found</h1>\n</html>\n'
    },
    'nginx_502': {
        'pattern': r'ERROR.*Failed to download image from',
        'detail': r'detail: <html>\r\n<head><title>502 Bad Gateway</title></head>\r\n<body>\r\n<center><h1>502 Bad Gateway</h1></center>\r\n<hr><center>nginx</center>\r\n</body>\r\n</html>\r\n '
    },
    'connection': {
        'pattern': r'ERROR.*error, connect point url error, cur images index',
        'detail': r'detail:(.+)'
    },
    'success_download': {
        'pattern': r'DEBUG.*Image saved as',
        'detail': r'cur txt images download count: (\d+)'
    },
    'cannot_open_image': {
        'pattern': r'ERROR.*无法打开图片',
        'detail': r'错误信息:*(\d+)'
    },
    'unknown_category': {
        'pattern': r'WARNING.*未知种类图片，待定:',
        'detail': r'(\d{4}\.jpg|png|gif)$'
    },
    'establish': {
        'pattern': 'ERROR.*unknown error',
        'detail': r'detail:(.+)'
    }
}

@logger.catch
def analyze_log_errors(file_path: str, error_pattern: str, detail_pattern: str) -> Tuple[Counter, str]:
    """Analyze log file for errors and their details
    
    Args:
        file_path: Path to log file
        error_pattern: Regex pattern to match errors
        detail_pattern: Regex pattern to match error details
        
    Returns:
        Tuple containing error counts and error pattern
    """
    error_counts = Counter()
    detail_causes: Dict[str, int] = {}

    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if re.search(error_pattern, line):
                error_counts['error'] += 1
                if detail_match := re.search(detail_pattern, line):
                    detail = detail_match.group(1).strip()
                    detail_causes[detail] = detail_causes.get(detail, 0) + 1

    return error_counts, error_pattern

@logger.catch
def log_analyze(log_file_path: str) -> Tuple[List, List]:
    """Analyze a log file for all error types
    
    Args:
        log_file_path: Path to log file
        
    Returns:
        Tuple containing lists of error counts and error details
    """
    error_list = []
    error_detail_list = []
    
    for error_type in ERROR_PATTERNS.values():
        counts, details = analyze_log_errors(
            log_file_path,
            error_type['pattern'],
            error_type['detail']
        )
        error_list.append(counts)
        error_detail_list.append(details)
        
    return error_list, error_detail_list

@logger.catch
def find_log(directory: str) -> List[str]:
    """Find all log files in directory
    
    Args:
        directory: Directory to search
        
    Returns:
        List of log file paths
    """
    log_dir = Path(directory)
    if not log_dir.exists():
        log_dir.mkdir(parents=True)
        logger.info(f"Created directory: {log_dir}")
        
    return [str(f) for f in log_dir.rglob('*.log')]

@logger.catch
def log_data_analyze() -> List[List]:
    """Analyze all logs in log directory
    
    Returns:
        List of analysis results for each log
    """
    log_dir = Path('./log_dir').resolve()
    log_files = find_log(str(log_dir))
    
    log_analyze_data = []
    for log_file in log_files:
        result_counts, result_details = log_analyze(log_file)
        log_analyze_data.append([
            result_counts,
            result_details,
            log_file
        ])
        
    logger.info(f"Scanned {len(log_files)} log files")
    return log_analyze_data

@logger.catch
def log_analyze_data_output() -> List[List]:
    """Process and format log analysis data
    
    Returns:
        Formatted analysis results
    """
    data = log_data_analyze()
    results = []
    
    for log_data in data:
        file_name = log_data[2]
        error_counts = log_data[0]
        error_details = log_data[1]
        
        error_names = []
        error_counts_list = []
        skip_indices = []
        
        for i, count in enumerate(error_counts):
            if count['error']:
                error_counts_list.append(count['error'])
            else:
                skip_indices.append(i)
                
        for i, detail in enumerate(error_details):
            if i not in skip_indices and detail:
                error_names.append(detail[7:])
                
        if error_counts_list and error_names:
            names, counts = merge_same_value(error_names, error_counts_list)
            result = [names, counts]
            if file_name:
                result.append(file_name)
            results.append(result)
            
    return results

@logger.catch
def log_analyze_data_output_new() -> Tuple[List[str], List[int]]:
    """分析日志文件"""
    # Values should be numeric
    error_counts = [28, 126, 1244]
    
    # Labels should be strings
    error_names = ["Connection Error", "Timeout Error", "Download Error"]
    
    return error_names, error_counts

@logger.catch
def merge_same_value(labels: List[str], values: List[int]) -> Tuple[List, List]:
    """Merge duplicate labels and sum their values
    
    Args:
        labels: List of labels
        values: List of corresponding values
        
    Returns:
        Tuple of merged labels and values
    """
    if len(labels) != len(values):
        raise ValueError("Labels and values must have same length")
        
    merged = {}
    for label, value in zip(labels, values):
        merged[label] = merged.get(label, 0) + value
        
    return list(merged.keys()), list(merged.values())
