# -*- coding: utf-8 -*-
# Copyright [2015] [Robert Allen]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import
import requests
import requests.auth
from collections import namedtuple
import httplib2
import httplib
import sys

try:
    import collectd
except ImportError:
    """MoveAlong Along, We assume we are testing"""
    # Todo Add some error checking to the collectd.* use cases.

# todo more logging
VERBOSE_LOGGING = False
COLLECTD_PLUGIN_NAMESPACE = "aurora-scheduler"

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                        httplib.IncompleteRead, httplib.ImproperConnectionState,
                        httplib.CannotSendRequest, httplib.CannotSendHeader,
                        httplib.ResponseNotReady, httplib.BadStatusLine)

TASK_ID = "[a-zA-Z-_.]+/[a-zA-Z-_.]+/[a-zA-Z-_.]+_"
RACK_ID = "[a-zA-Z-_]+"
Stat = namedtuple('Stat', ('type', 'name'))

CONFIGS = []
# Todo will need to access that the metrics all have the right value types ie gauge, counter etc
METRICS = {
    # Async Tasks
    "async_tasks_completed": Stat("counter", "async_tasks_completed"),
    # Attributes
    "attribute_store_fetch_all_events": Stat("counter", "attribute_store_fetch_all_events"),
    "attribute_store_fetch_all_events_per_sec": Stat("gauge", "attribute_store_fetch_all_events_per_sec"),
    "attribute_store_fetch_all_nanos_per_event": Stat("gauge", "attribute_store_fetch_all_nanos_per_event"),
    "attribute_store_fetch_all_nanos_total": Stat("counter", "attribute_store_fetch_all_nanos_total"),
    "attribute_store_fetch_all_nanos_total_per_sec": Stat("gauge", "attribute_store_fetch_all_nanos_total_per_sec"),
    "attribute_store_fetch_one_events": Stat("counter", "attribute_store_fetch_one_events"),
    "attribute_store_fetch_one_events_per_sec": Stat("gauge", "attribute_store_fetch_one_events_per_sec"),
    "attribute_store_fetch_one_nanos_per_event": Stat("gauge", "attribute_store_fetch_one_nanos_per_event"),
    "attribute_store_fetch_one_nanos_total": Stat("counter", "attribute_store_fetch_one_nanos_total"),
    "attribute_store_fetch_one_nanos_total_per_sec": Stat("gauge", "attribute_store_fetch_one_nanos_total_per_sec"),
    "attribute_store_save_events": Stat("counter", "attribute_store_save_events"),
    "attribute_store_save_events_per_sec": Stat("gauge", "attribute_store_save_events_per_sec"),
    "attribute_store_save_nanos_per_event": Stat("gauge", "attribute_store_save_nanos_per_event"),
    "attribute_store_save_nanos_total": Stat("counter", "attribute_store_save_nanos_total"),
    "attribute_store_save_nanos_total_per_sec": Stat("gauge", "attribute_store_save_nanos_total_per_sec"),
    # Cron Jobs
    "cron_job_collisions": Stat("counter", "cron_job_collisions"),
    "cron_job_launch_failures": Stat("gauge", "cron_job_launch_failures"),
    "cron_job_misfires": Stat("gauge", "cron_job_misfires"),
    "cron_job_parse_failures": Stat("gauge", "cron_job_parse_failures"),
    "cron_job_triggers": Stat("counter", "cron_job_triggers"),
    "cron_jobs_loaded": Stat("gauge", "cron_jobs_loaded"),
    # Scheduling
    "dropped_update_events": Stat("gauge", "dropped_update_events"),
    "empty_slots_dedicated_large": Stat("gauge", "empty_slots_dedicated_large"),
    "empty_slots_dedicated_medium": Stat("gauge", "empty_slots_dedicated_medium"),
    "empty_slots_dedicated_small": Stat("gauge", "empty_slots_dedicated_small"),
    "empty_slots_dedicated_xlarge": Stat("gauge", "empty_slots_dedicated_xlarge"),
    "empty_slots_large": Stat("gauge", "empty_slots_large"),
    "empty_slots_medium": Stat("gauge", "empty_slots_medium"),
    "empty_slots_small": Stat("counter", "empty_slots_small"),
    "empty_slots_xlarge": Stat("gauge", "empty_slots_xlarge"),
    # Registered
    "framework_registered": Stat("gauge", "framework_registered"),
    "gc_executor_tasks_lost": Stat("gauge", "gc_executor_tasks_lost"),
    # Events
    "http_200_responses_events": Stat("counter", "_responses_events"),
    "http_200_responses_events_per_sec": Stat("gauge", "http_200_responses_events_per_sec"),
    "http_200_responses_nanos_per_event": Stat("gauge", "http_200_responses_nanos_per_event"),
    "http_200_responses_nanos_total": Stat("counter", "http_200_responses_nanos_total"),
    "http_200_responses_nanos_total_per_sec": Stat("gauge", "http_200_responses_nanos_total_per_sec"),
    # Job
    "job_store_task_config_keys_backfilled": Stat("gauge", "job_store_task_config_keys_backfilled"),
    "job_update_delete_errors": Stat("gauge", "job_update_delete_errors"),
    "job_update_recovery_errors": Stat("gauge", "job_update_recovery_errors"),
    "job_update_state_change_errors": Stat("gauge", "job_update_state_change_errors"),
    "job_update_store_delete_all_events": Stat("gauge", "job_update_store_delete_all_events"),
    "job_update_store_delete_all_events_per_sec": Stat("gauge", "job_update_store_delete_all_events_per_sec"),
    "job_update_store_delete_all_nanos_per_event": Stat("gauge", "job_update_store_delete_all_nanos_per_event"),
    "job_update_store_delete_all_nanos_total": Stat("counter", "job_update_store_delete_all_nanos_total"),
    "job_update_store_delete_all_nanos_total_per_sec": Stat("gauge", "job_update_store_delete_all_nanos_total_per_sec"),
    "job_update_store_fetch_all_details_events": Stat("counter", "job_update_store_fetch_all_details_events"),
    "job_update_store_fetch_all_details_events_per_sec": Stat("gauge",
                                                              "job_update_store_fetch_all_details_events_per_sec"),
    "job_update_store_fetch_all_details_nanos_per_event": Stat("gauge",
                                                               "job_update_store_fetch_all_details_nanos_per_event"),
    "job_update_store_fetch_all_details_nanos_total": Stat("counter", "job_update_store_fetch_all_details_nanos_total"),
    "job_update_store_fetch_all_details_nanos_total_per_sec": Stat("gauge",
                                                                   "job_update_store_fetch_all_details_nanos_total_per_sec"),
    "job_update_store_fetch_details_list_events": Stat("gauge", "job_update_store_fetch_details_list_events"),
    "job_update_store_fetch_details_list_events_per_sec": Stat("gauge",
                                                               "job_update_store_fetch_details_list_events_per_sec"),
    "job_update_store_fetch_details_list_nanos_per_event": Stat("gauge",
                                                                "job_update_store_fetch_details_list_nanos_per_event"),
    "job_update_store_fetch_details_list_nanos_total": Stat("counter",
                                                            "job_update_store_fetch_details_list_nanos_total"),
    "job_update_store_fetch_details_list_nanos_total_per_sec": Stat("gauge",
                                                                    "job_update_store_fetch_details_list_nanos_total_per_sec"),
    "job_update_store_fetch_summaries_events": Stat("counter", "job_update_store_fetch_summaries_events"),
    "job_update_store_fetch_summaries_events_per_sec": Stat("gauge", "job_update_store_fetch_summaries_events_per_sec"),
    "job_update_store_fetch_summaries_nanos_per_event": Stat("gauge",
                                                             "job_update_store_fetch_summaries_nanos_per_event"),
    "job_update_store_fetch_summaries_nanos_total": Stat("counter", "job_update_store_fetch_summaries_nanos_total"),
    "job_update_store_fetch_summaries_nanos_total_per_sec": Stat("gauge",
                                                                 "job_update_store_fetch_summaries_nanos_total_per_sec"),
    "job_update_store_prune_history_events": Stat("counter", "job_update_store_prune_history_events"),
    "job_update_store_prune_history_events_per_sec": Stat("gauge", "job_update_store_prune_history_events_per_sec"),
    "job_update_store_prune_history_nanos_per_event": Stat("gauge", "job_update_store_prune_history_nanos_per_event"),
    "job_update_store_prune_history_nanos_total": Stat("counter", "job_update_store_prune_history_nanos_total"),
    "job_update_store_prune_history_nanos_total_per_sec": Stat("gauge",
                                                               "job_update_store_prune_history_nanos_total_per_sec"),
    # JVM
    "jvm_available_processors": Stat("gauge", "jvm_available_processors"),
    "jvm_class_loaded_count": Stat("counter", "jvm_class_loaded_count"),
    "jvm_class_total_loaded_count": Stat("counter", "jvm_class_total_loaded_count"),
    "jvm_class_unloaded_count": Stat("gauge", "jvm_class_unloaded_count"),
    "jvm_gc_PS_MarkSweep_collection_count": Stat("gauge", "jvm_gc_PS_MarkSweep_collection_count"),
    "jvm_gc_PS_MarkSweep_collection_time_ms": Stat("counter", "jvm_gc_PS_MarkSweep_collection_time_ms"),
    "jvm_gc_PS_Scavenge_collection_count": Stat("counter", "jvm_gc_PS_Scavenge_collection_count"),
    "jvm_gc_PS_Scavenge_collection_time_ms": Stat("counter", "jvm_gc_PS_Scavenge_collection_time_ms"),
    "jvm_gc_collection_count": Stat("counter", "jvm_gc_collection_count"),
    "jvm_gc_collection_time_ms": Stat("counter", "jvm_gc_collection_time_ms"),
    "jvm_memory_free_mb": Stat("counter", "jvm_memory_free_mb"),
    "jvm_memory_heap_mb_committed": Stat("counter", "jvm_memory_heap_mb_committed"),
    "jvm_memory_heap_mb_max": Stat("counter", "jvm_memory_heap_mb_max"),
    "jvm_memory_heap_mb_used": Stat("counter", "jvm_memory_heap_mb_used"),
    "jvm_memory_max_mb": Stat("counter", "jvm_memory_max_mb"),
    "jvm_memory_mb_total": Stat("counter", "jvm_memory_mb_total"),
    "jvm_memory_non_heap_mb_committed": Stat("counter", "jvm_memory_non_heap_mb_committed"),
    "jvm_memory_non_heap_mb_max": Stat("gauge", "jvm_memory_non_heap_mb_max"),
    "jvm_memory_non_heap_mb_used": Stat("counter", "jvm_memory_non_heap_mb_used"),
    "jvm_threads_active": Stat("counter", "jvm_threads_active"),
    "jvm_threads_daemon": Stat("counter", "jvm_threads_daemon"),
    "jvm_threads_peak": Stat("counter", "jvm_threads_peak"),
    "jvm_threads_started": Stat("counter", "jvm_threads_started"),
    "jvm_time_ms": Stat("counter", "jvm_time_ms"),
    "jvm_uptime_secs": Stat("counter", "jvm_uptime_secs"),
    # Locks
    "lock_store_delete_locks_events": Stat("gauge", "lock_store_delete_locks_events"),
    "lock_store_delete_locks_events_per_sec": Stat("gauge", "lock_store_delete_locks_events_per_sec"),
    "lock_store_delete_locks_nanos_per_event": Stat("gauge", "lock_store_delete_locks_nanos_per_event"),
    "lock_store_delete_locks_nanos_total": Stat("counter", "lock_store_delete_locks_nanos_total"),
    "lock_store_delete_locks_nanos_total_per_sec": Stat("gauge", "lock_store_delete_locks_nanos_total_per_sec"),
    "lock_store_fetch_lock_events": Stat("counter", "lock_store_fetch_lock_events"),
    "lock_store_fetch_lock_events_per_sec": Stat("gauge", "lock_store_fetch_lock_events_per_sec"),
    "lock_store_fetch_lock_nanos_per_event": Stat("gauge", "lock_store_fetch_lock_nanos_per_event"),
    "lock_store_fetch_lock_nanos_total": Stat("counter", "lock_store_fetch_lock_nanos_total"),
    "lock_store_fetch_lock_nanos_total_per_sec": Stat("gauge", "lock_store_fetch_lock_nanos_total_per_sec"),
    "lock_store_fetch_locks_events": Stat("counter", "lock_store_fetch_locks_events"),
    "lock_store_fetch_locks_events_per_sec": Stat("gauge", "lock_store_fetch_locks_events_per_sec"),
    "lock_store_fetch_locks_nanos_per_event": Stat("gauge", "lock_store_fetch_locks_nanos_per_event"),
    "lock_store_fetch_locks_nanos_total": Stat("counter", "lock_store_fetch_locks_nanos_total"),
    "lock_store_fetch_locks_nanos_total_per_sec": Stat("gauge", "lock_store_fetch_locks_nanos_total_per_sec"),
    "lock_store_remove_lock_events": Stat("gauge", "lock_store_remove_lock_events"),
    "lock_store_remove_lock_events_per_sec": Stat("gauge", "lock_store_remove_lock_events_per_sec"),
    "lock_store_remove_lock_nanos_per_event": Stat("gauge", "lock_store_remove_lock_nanos_per_event"),
    "lock_store_remove_lock_nanos_total": Stat("counter", "lock_store_remove_lock_nanos_total"),
    "lock_store_remove_lock_nanos_total_per_sec": Stat("gauge", "lock_store_remove_lock_nanos_total_per_sec"),
    "lock_store_save_lock_events": Stat("gauge", "lock_store_save_lock_events"),
    "lock_store_save_lock_events_per_sec": Stat("gauge", "lock_store_save_lock_events_per_sec"),
    "lock_store_save_lock_nanos_per_event": Stat("gauge", "lock_store_save_lock_nanos_per_event"),
    "lock_store_save_lock_nanos_total": Stat("counter", "lock_store_save_lock_nanos_total"),
    "lock_store_save_lock_nanos_total_per_sec": Stat("gauge", "lock_store_save_lock_nanos_total_per_sec"),
    # Logging
    "log_entry_serialize_events": Stat("counter", "log_entry_serialize_events"),
    "log_entry_serialize_events_per_sec": Stat("gauge", "log_entry_serialize_events_per_sec"),
    "log_entry_serialize_nanos_per_event": Stat("gauge", "log_entry_serialize_nanos_per_event"),
    "log_entry_serialize_nanos_total": Stat("counter", "log_entry_serialize_nanos_total"),
    "log_entry_serialize_nanos_total_per_sec": Stat("gauge", "log_entry_serialize_nanos_total_per_sec"),
    "log_manager_append_events": Stat("counter", "log_manager_append_events"),
    "log_manager_append_events_per_sec": Stat("gauge", "log_manager_append_events_per_sec"),
    "log_manager_append_nanos_per_event": Stat("gauge", "log_manager_append_nanos_per_event"),
    "log_manager_append_nanos_total": Stat("counter", "log_manager_append_nanos_total"),
    "log_manager_append_nanos_total_per_sec": Stat("gauge", "log_manager_append_nanos_total_per_sec"),
    "log_manager_deflate_events": Stat("counter", "log_manager_deflate_events"),
    "log_manager_deflate_events_per_sec": Stat("gauge", "log_manager_deflate_events_per_sec"),
    "log_manager_deflate_nanos_per_event": Stat("gauge", "log_manager_deflate_nanos_per_event"),
    "log_manager_deflate_nanos_total": Stat("counter", "log_manager_deflate_nanos_total"),
    "log_manager_deflate_nanos_total_per_sec": Stat("gauge", "log_manager_deflate_nanos_total_per_sec"),
    "log_manager_snapshot_events": Stat("counter", "log_manager_snapshot_events"),
    "log_manager_snapshot_events_per_sec": Stat("gauge", "log_manager_snapshot_events_per_sec"),
    "log_manager_snapshot_nanos_per_event": Stat("gauge", "log_manager_snapshot_nanos_per_event"),
    "log_manager_snapshot_nanos_total": Stat("counter", "log_manager_snapshot_nanos_total"),
    "log_manager_snapshot_nanos_total_per_sec": Stat("gauge", "log_manager_snapshot_nanos_total_per_sec"),
    "log_storage_write_lock_wait_events": Stat("counter", "log_storage_write_lock_wait_events"),
    "log_storage_write_lock_wait_events_per_sec": Stat("gauge", "log_storage_write_lock_wait_events_per_sec"),
    "log_storage_write_lock_wait_ns_per_event": Stat("gauge", "log_storage_write_lock_wait_ns_per_event"),
    "log_storage_write_lock_wait_ns_total": Stat("counter", "log_storage_write_lock_wait_ns_total"),
    "log_storage_write_lock_wait_ns_total_per_sec": Stat("gauge", "log_storage_write_lock_wait_ns_total_per_sec"),
    # Memory
    "mem_storage_delete_all_tasks_events": Stat("gauge", "mem_storage_delete_all_tasks_events"),
    "mem_storage_delete_all_tasks_events_per_sec": Stat("gauge", "mem_storage_delete_all_tasks_events_per_sec"),
    "mem_storage_delete_all_tasks_nanos_per_event": Stat("gauge", "mem_storage_delete_all_tasks_nanos_per_event"),
    "mem_storage_delete_all_tasks_nanos_total": Stat("counter", "mem_storage_delete_all_tasks_nanos_total"),
    "mem_storage_delete_all_tasks_nanos_total_per_sec": Stat("gauge",
                                                             "mem_storage_delete_all_tasks_nanos_total_per_sec"),
    "mem_storage_delete_tasks_events": Stat("counter", "mem_storage_delete_tasks_events"),
    "mem_storage_delete_tasks_events_per_sec": Stat("gauge", "mem_storage_delete_tasks_events_per_sec"),
    "mem_storage_delete_tasks_nanos_per_event": Stat("gauge", "mem_storage_delete_tasks_nanos_per_event"),
    "mem_storage_delete_tasks_nanos_total": Stat("counter", "mem_storage_delete_tasks_nanos_total"),
    "mem_storage_delete_tasks_nanos_total_per_sec": Stat("gauge", "mem_storage_delete_tasks_nanos_total_per_sec"),
    "mem_storage_fetch_tasks_events": Stat("counter", "mem_storage_fetch_tasks_events"),
    "mem_storage_fetch_tasks_events_per_sec": Stat("gauge", "mem_storage_fetch_tasks_events_per_sec"),
    "mem_storage_fetch_tasks_nanos_per_event": Stat("gauge", "mem_storage_fetch_tasks_nanos_per_event"),
    "mem_storage_fetch_tasks_nanos_total": Stat("counter", "mem_storage_fetch_tasks_nanos_total"),
    "mem_storage_fetch_tasks_nanos_total_per_sec": Stat("gauge", "mem_storage_fetch_tasks_nanos_total_per_sec"),
    "mem_storage_mutate_tasks_events": Stat("counter", "mem_storage_mutate_tasks_events"),
    "mem_storage_mutate_tasks_events_per_sec": Stat("gauge", "mem_storage_mutate_tasks_events_per_sec"),
    "mem_storage_mutate_tasks_nanos_per_event": Stat("gauge", "mem_storage_mutate_tasks_nanos_per_event"),
    "mem_storage_mutate_tasks_nanos_total": Stat("counter", "mem_storage_mutate_tasks_nanos_total"),
    "mem_storage_mutate_tasks_nanos_total_per_sec": Stat("gauge", "mem_storage_mutate_tasks_nanos_total_per_sec"),
    "mem_storage_read_operation_events": Stat("counter", "mem_storage_read_operation_events"),
    "mem_storage_read_operation_events_per_sec": Stat("gauge", "mem_storage_read_operation_events_per_sec"),
    "mem_storage_read_operation_nanos_per_event": Stat("gauge", "mem_storage_read_operation_nanos_per_event"),
    "mem_storage_read_operation_nanos_total": Stat("counter", "mem_storage_read_operation_nanos_total"),
    "mem_storage_read_operation_nanos_total_per_sec": Stat("gauge", "mem_storage_read_operation_nanos_total_per_sec"),
    "mem_storage_save_tasks_events": Stat("counter", "mem_storage_save_tasks_events"),
    "mem_storage_save_tasks_events_per_sec": Stat("gauge", "mem_storage_save_tasks_events_per_sec"),
    "mem_storage_save_tasks_nanos_per_event": Stat("gauge", "mem_storage_save_tasks_nanos_per_event"),
    "mem_storage_save_tasks_nanos_total": Stat("counter", "mem_storage_save_tasks_nanos_total"),
    "mem_storage_save_tasks_nanos_total_per_sec": Stat("gauge", "mem_storage_save_tasks_nanos_total_per_sec"),
    "mem_storage_write_operation_events": Stat("counter", "mem_storage_write_operation_events"),
    "mem_storage_write_operation_events_per_sec": Stat("gauge", "mem_storage_write_operation_events_per_sec"),
    "mem_storage_write_operation_nanos_per_event": Stat("gauge", "mem_storage_write_operation_nanos_per_event"),
    "mem_storage_write_operation_nanos_total": Stat("counter", "mem_storage_write_operation_nanos_total"),
    "mem_storage_write_operation_nanos_total_per_sec": Stat("gauge", "mem_storage_write_operation_nanos_total_per_sec"),
    # Offer
    "offer_accept_races": Stat("gauge", "offer_accept_races"),
    "offer_queue_accept_offer_events": Stat("counter", "offer_queue_accept_offer_events"),
    "offer_queue_accept_offer_events_per_sec": Stat("gauge", "offer_queue_accept_offer_events_per_sec"),
    "offer_queue_accept_offer_nanos_per_event": Stat("gauge", "offer_queue_accept_offer_nanos_per_event"),
    "offer_queue_accept_offer_nanos_total": Stat("counter", "offer_queue_accept_offer_nanos_total"),
    "offer_queue_accept_offer_nanos_total_per_sec": Stat("gauge", "offer_queue_accept_offer_nanos_total_per_sec"),
    "offer_queue_launch_first_events": Stat("counter", "offer_queue_launch_first_events"),
    "offer_queue_launch_first_events_per_sec": Stat("gauge", "offer_queue_launch_first_events_per_sec"),
    "offer_queue_launch_first_nanos_per_event": Stat("gauge", "offer_queue_launch_first_nanos_per_event"),
    "offer_queue_launch_first_nanos_total": Stat("counter", "offer_queue_launch_first_nanos_total"),
    "offer_queue_launch_first_nanos_total_per_sec": Stat("gauge", "offer_queue_launch_first_nanos_total_per_sec"),
    "outstanding_offers": Stat("gauge", "outstanding_offers"),
    # Prememptor
    "preemption_slot_cache_size": Stat("gauge", "preemption_slot_cache_size"),
    "preemptor_missing_attributes": Stat("gauge", "preemptor_missing_attributes"),
    "preemptor_slot_search_attempts_for_non_prod": Stat("gauge", "preemptor_slot_search_attempts_for_non_prod"),
    "preemptor_slot_search_attempts_for_prod": Stat("gauge", "preemptor_slot_search_attempts_for_prod"),
    "preemptor_slot_search_failed_for_non_prod": Stat("gauge", "preemptor_slot_search_failed_for_non_prod"),
    "preemptor_slot_search_failed_for_prod": Stat("gauge", "preemptor_slot_search_failed_for_prod"),
    "preemptor_slot_search_successful_for_non_prod": Stat("gauge", "preemptor_slot_search_successful_for_non_prod"),
    "preemptor_slot_search_successful_for_prod": Stat("gauge", "preemptor_slot_search_successful_for_prod"),
    "preemptor_slot_validation_failed": Stat("gauge", "preemptor_slot_validation_failed"),
    "preemptor_slot_validation_successful": Stat("gauge", "preemptor_slot_validation_successful"),
    "preemptor_tasks_preempted_non_prod": Stat("gauge", "preemptor_tasks_preempted_non_prod"),
    "preemptor_tasks_preempted_prod": Stat("gauge", "preemptor_tasks_preempted_prod"),
    # Process
    "process_cpu_cores_utilized": Stat("gauge", "process_cpu_cores_utilized"),
    "process_cpu_time_nanos": Stat("counter", "process_cpu_time_nanos"),
    "process_max_fd_count": Stat("counter", "process_max_fd_count"),
    "process_open_fd_count": Stat("counter", "process_open_fd_count"),
    # Executor PubSub
    "pubsub_executor_queue_size": Stat("gauge", "pubsub_executor_queue_size"),
    # Quartx Scheduling
    "quartz_scheduler_running": Stat("gauge", "quartz_scheduler_running"),
    # Quota
    "quota_store_delete_quotas_events": Stat("gauge", "quota_store_delete_quotas_events"),
    "quota_store_delete_quotas_events_per_sec": Stat("gauge", "quota_store_delete_quotas_events_per_sec"),
    "quota_store_delete_quotas_nanos_per_event": Stat("gauge", "quota_store_delete_quotas_nanos_per_event"),
    "quota_store_delete_quotas_nanos_total": Stat("counter", "quota_store_delete_quotas_nanos_total"),
    "quota_store_delete_quotas_nanos_total_per_sec": Stat("gauge", "quota_store_delete_quotas_nanos_total_per_sec"),
    "quota_store_fetch_quota_events": Stat("counter", "quota_store_fetch_quota_events"),
    "quota_store_fetch_quota_events_per_sec": Stat("gauge", "quota_store_fetch_quota_events_per_sec"),
    "quota_store_fetch_quota_nanos_per_event": Stat("gauge", "quota_store_fetch_quota_nanos_per_event"),
    "quota_store_fetch_quota_nanos_total": Stat("counter", "quota_store_fetch_quota_nanos_total"),
    "quota_store_fetch_quota_nanos_total_per_sec": Stat("gauge", "quota_store_fetch_quota_nanos_total_per_sec"),
    "quota_store_fetch_quotas_events": Stat("counter", "quota_store_fetch_quotas_events"),
    "quota_store_fetch_quotas_events_per_sec": Stat("gauge", "quota_store_fetch_quotas_events_per_sec"),
    "quota_store_fetch_quotas_nanos_per_event": Stat("gauge", "quota_store_fetch_quotas_nanos_per_event"),
    "quota_store_fetch_quotas_nanos_total": Stat("counter", "quota_store_fetch_quotas_nanos_total"),
    "quota_store_fetch_quotas_nanos_total_per_sec": Stat("gauge", "quota_store_fetch_quotas_nanos_total_per_sec"),
    "quota_store_save_quota_events": Stat("gauge", "quota_store_save_quota_events"),
    "quota_store_save_quota_events_per_sec": Stat("gauge", "quota_store_save_quota_events_per_sec"),
    "quota_store_save_quota_nanos_per_event": Stat("gauge", "quota_store_save_quota_nanos_per_event"),
    "quota_store_save_quota_nanos_total": Stat("counter", "quota_store_save_quota_nanos_total"),
    "quota_store_save_quota_nanos_total_per_sec": Stat("gauge", "quota_store_save_quota_nanos_total_per_sec"),
    # Reservation
    "reservation_cache_size": Stat("gauge", "reservation_cache_size"),
    # Resources
    "resources_allocated_quota_cpu": Stat("counter", "resources_allocated_quota_cpu"),
    "resources_allocated_quota_disk_gb": Stat("counter", "resources_allocated_quota_disk_gb"),
    "resources_allocated_quota_ram_gb": Stat("counter", "resources_allocated_quota_ram_gb"),
    "resources_dedicated_consumed_cpu": Stat("gauge", "resources_dedicated_consumed_cpu"),
    "resources_dedicated_consumed_disk_gb": Stat("gauge", "resources_dedicated_consumed_disk_gb"),
    "resources_dedicated_consumed_ram_gb": Stat("gauge", "resources_dedicated_consumed_ram_gb"),
    "resources_free_pool_consumed_cpu": Stat("gauge", "resources_free_pool_consumed_cpu"),
    "resources_free_pool_consumed_disk_gb": Stat("counter", "resources_free_pool_consumed_disk_gb"),
    "resources_free_pool_consumed_ram_gb": Stat("counter", "resources_free_pool_consumed_ram_gb"),
    "resources_quota_consumed_cpu": Stat("gauge", "resources_quota_consumed_cpu"),
    "resources_quota_consumed_disk_gb": Stat("gauge", "resources_quota_consumed_disk_gb"),
    "resources_quota_consumed_ram_gb": Stat("gauge", "resources_quota_consumed_ram_gb"),
    "resources_total_consumed_cpu": Stat("gauge", "resources_total_consumed_cpu"),
    "resources_total_consumed_disk_gb": Stat("counter", "resources_total_consumed_disk_gb"),
    "resources_total_consumed_ram_gb": Stat("counter", "resources_total_consumed_ram_gb"),
    # Shedule{,d,er,ing}
    "schedule_attempts_failed": Stat("gauge", "schedule_attempts_failed"),
    "schedule_attempts_fired": Stat("counter", "schedule_attempts_fired"),
    "schedule_attempts_no_match": Stat("counter", "schedule_attempts_no_match"),
    "schedule_queue_size": Stat("gauge", "schedule_queue_size"),
    "scheduled_task_penalty_events": Stat("counter", "scheduled_task_penalty_events"),
    "scheduled_task_penalty_events_per_sec": Stat("gauge", "scheduled_task_penalty_events_per_sec"),
    "scheduled_task_penalty_ms_per_event": Stat("gauge", "scheduled_task_penalty_ms_per_event"),
    "scheduled_task_penalty_ms_total": Stat("counter", "scheduled_task_penalty_ms_total"),
    "scheduled_task_penalty_ms_total_per_sec": Stat("gauge", "scheduled_task_penalty_ms_total_per_sec"),
    "scheduler_backup_failed": Stat("gauge", "scheduler_backup_failed"),
    "scheduler_backup_success": Stat("counter", "scheduler_backup_success"),
    "scheduler_driver_kill_failures": Stat("gauge", "scheduler_driver_kill_failures"),
    "scheduler_gc_insufficient_offers": Stat("counter", "scheduler_gc_insufficient_offers"),
    "scheduler_gc_offers_consumed": Stat("counter", "scheduler_gc_offers_consumed"),
    "scheduler_gc_tasks_created": Stat("counter", "scheduler_gc_tasks_created"),
    "scheduler_illegal_task_state_transitions": Stat("gauge", "scheduler_illegal_task_state_transitions"),
    "scheduler_lifecycle_ACTIVE": Stat("gauge", "scheduler_lifecycle_ACTIVE"),
    "scheduler_lifecycle_DEAD": Stat("gauge", "scheduler_lifecycle_DEAD"),
    "scheduler_lifecycle_IDLE": Stat("gauge", "scheduler_lifecycle_IDLE"),
    "scheduler_lifecycle_LEADER_AWAITING_REGISTRATION": Stat("gauge",
                                                             "scheduler_lifecycle_LEADER_AWAITING_REGISTRATION"),
    "scheduler_lifecycle_PREPARING_STORAGE": Stat("gauge", "scheduler_lifecycle_PREPARING_STORAGE"),
    "scheduler_lifecycle_STORAGE_PREPARED": Stat("gauge", "scheduler_lifecycle_STORAGE_PREPARED"),
    "scheduler_log_bad_frames_read": Stat("gauge", "scheduler_log_bad_frames_read"),
    "scheduler_log_bytes_read": Stat("counter", "scheduler_log_bytes_read"),
    "scheduler_log_bytes_written": Stat("counter", "scheduler_log_bytes_written"),
    "scheduler_log_deflated_entries_read": Stat("gauge", "scheduler_log_deflated_entries_read"),
    "scheduler_log_entries_read": Stat("counter", "scheduler_log_entries_read"),
    "scheduler_log_entries_written": Stat("counter", "scheduler_log_entries_written"),
    "scheduler_log_native_append_events": Stat("counter", "scheduler_log_native_append_events"),
    "scheduler_log_native_append_events_per_sec": Stat("gauge", "scheduler_log_native_append_events_per_sec"),
    "scheduler_log_native_append_failures": Stat("gauge", "scheduler_log_native_append_failures"),
    "scheduler_log_native_append_nanos_per_event": Stat("gauge", "scheduler_log_native_append_nanos_per_event"),
    "scheduler_log_native_append_nanos_total": Stat("counter", "scheduler_log_native_append_nanos_total"),
    "scheduler_log_native_append_nanos_total_per_sec": Stat("gauge", "scheduler_log_native_append_nanos_total_per_sec"),
    "scheduler_log_native_append_timeouts": Stat("gauge", "scheduler_log_native_append_timeouts"),
    "scheduler_log_native_native_entries_skipped": Stat("gauge", "scheduler_log_native_native_entries_skipped"),
    "scheduler_log_native_read_events": Stat("counter", "scheduler_log_native_read_events"),
    "scheduler_log_native_read_events_per_sec": Stat("gauge", "scheduler_log_native_read_events_per_sec"),
    "scheduler_log_native_read_failures": Stat("gauge", "scheduler_log_native_read_failures"),
    "scheduler_log_native_read_nanos_per_event": Stat("gauge", "scheduler_log_native_read_nanos_per_event"),
    "scheduler_log_native_read_nanos_total": Stat("counter", "scheduler_log_native_read_nanos_total"),
    "scheduler_log_native_read_nanos_total_per_sec": Stat("gauge", "scheduler_log_native_read_nanos_total_per_sec"),
    "scheduler_log_native_read_timeouts": Stat("gauge", "scheduler_log_native_read_timeouts"),
    "scheduler_log_native_truncate_events": Stat("counter", "scheduler_log_native_truncate_events"),
    "scheduler_log_native_truncate_events_per_sec": Stat("gauge", "scheduler_log_native_truncate_events_per_sec"),
    "scheduler_log_native_truncate_failures": Stat("gauge", "scheduler_log_native_truncate_failures"),
    "scheduler_log_native_truncate_nanos_per_event": Stat("gauge", "scheduler_log_native_truncate_nanos_per_event"),
    "scheduler_log_native_truncate_nanos_total": Stat("counter", "scheduler_log_native_truncate_nanos_total"),
    "scheduler_log_native_truncate_nanos_total_per_sec": Stat("gauge",
                                                              "scheduler_log_native_truncate_nanos_total_per_sec"),
    "scheduler_log_native_truncate_timeouts": Stat("gauge", "scheduler_log_native_truncate_timeouts"),
    "scheduler_log_recover_events": Stat("gauge", "scheduler_log_recover_events"),
    "scheduler_log_recover_events_per_sec": Stat("gauge", "scheduler_log_recover_events_per_sec"),
    "scheduler_log_recover_nanos_per_event": Stat("gauge", "scheduler_log_recover_nanos_per_event"),
    "scheduler_log_recover_nanos_total": Stat("counter", "scheduler_log_recover_nanos_total"),
    "scheduler_log_recover_nanos_total_per_sec": Stat("gauge", "scheduler_log_recover_nanos_total_per_sec"),
    "scheduler_log_snapshot_events": Stat("counter", "scheduler_log_snapshot_events"),
    "scheduler_log_snapshot_events_per_sec": Stat("gauge", "scheduler_log_snapshot_events_per_sec"),
    "scheduler_log_snapshot_nanos_per_event": Stat("gauge", "scheduler_log_snapshot_nanos_per_event"),
    "scheduler_log_snapshot_nanos_total": Stat("counter", "scheduler_log_snapshot_nanos_total"),
    "scheduler_log_snapshot_nanos_total_per_sec": Stat("gauge", "scheduler_log_snapshot_nanos_total_per_sec"),
    "scheduler_log_snapshot_persist_events": Stat("counter", "scheduler_log_snapshot_persist_events"),
    "scheduler_log_snapshot_persist_events_per_sec": Stat("gauge", "scheduler_log_snapshot_persist_events_per_sec"),
    "scheduler_log_snapshot_persist_nanos_per_event": Stat("gauge", "scheduler_log_snapshot_persist_nanos_per_event"),
    "scheduler_log_snapshot_persist_nanos_total": Stat("counter", "scheduler_log_snapshot_persist_nanos_total"),
    "scheduler_log_snapshot_persist_nanos_total_per_sec": Stat("gauge",
                                                               "scheduler_log_snapshot_persist_nanos_total_per_sec"),
    "scheduler_log_snapshots": Stat("counter", "scheduler_log_snapshots"),
    "scheduler_log_un_snapshotted_transactions": Stat("counter", "scheduler_log_un_snapshotted_transactions"),
    "scheduler_resource_offers": Stat("counter", "scheduler_resource_offers"),
    "scheduler_resource_offers_events": Stat("counter", "scheduler_resource_offers_events"),
    "scheduler_resource_offers_events_per_sec": Stat("gauge", "scheduler_resource_offers_events_per_sec"),
    "scheduler_resource_offers_nanos_per_event": Stat("gauge", "scheduler_resource_offers_nanos_per_event"),
    "scheduler_resource_offers_nanos_total": Stat("counter", "scheduler_resource_offers_nanos_total"),
    "scheduler_resource_offers_nanos_total_per_sec": Stat("gauge", "scheduler_resource_offers_nanos_total_per_sec"),
    "scheduler_status_update_events": Stat("counter", "scheduler_status_update_events"),
    "scheduler_status_update_events_per_sec": Stat("gauge", "scheduler_status_update_events_per_sec"),
    "scheduler_status_update_nanos_per_event": Stat("gauge", "scheduler_status_update_nanos_per_event"),
    "scheduler_status_update_nanos_total": Stat("counter", "scheduler_status_update_nanos_total"),
    "scheduler_status_update_nanos_total_per_sec": Stat("gauge", "scheduler_status_update_nanos_total_per_sec"),
    "scheduler_store_fetch_framework_id_events": Stat("counter", "scheduler_store_fetch_framework_id_events"),
    "scheduler_store_fetch_framework_id_events_per_sec": Stat("gauge",
                                                              "scheduler_store_fetch_framework_id_events_per_sec"),
    "scheduler_store_fetch_framework_id_nanos_per_event": Stat("gauge",
                                                               "scheduler_store_fetch_framework_id_nanos_per_event"),
    "scheduler_store_fetch_framework_id_nanos_total": Stat("counter", "scheduler_store_fetch_framework_id_nanos_total"),
    "scheduler_store_fetch_framework_id_nanos_total_per_sec": Stat("gauge",
                                                                   "scheduler_store_fetch_framework_id_nanos_total_per_sec"),
    "scheduler_store_save_framework_id_events": Stat("gauge", "scheduler_store_save_framework_id_events"),
    "scheduler_store_save_framework_id_events_per_sec": Stat("gauge",
                                                             "scheduler_store_save_framework_id_events_per_sec"),
    "scheduler_store_save_framework_id_nanos_per_event": Stat("gauge",
                                                              "scheduler_store_save_framework_id_nanos_per_event"),
    "scheduler_store_save_framework_id_nanos_total": Stat("counter", "scheduler_store_save_framework_id_nanos_total"),
    "scheduler_store_save_framework_id_nanos_total_per_sec": Stat("gauge",
                                                                  "scheduler_store_save_framework_id_nanos_total_per_sec"),
    "scheduler_thrift_acquireLock_events": Stat("gauge", "scheduler_thrift_acquireLock_events"),
    "scheduler_thrift_acquireLock_events_per_sec": Stat("gauge", "scheduler_thrift_acquireLock_events_per_sec"),
    "scheduler_thrift_acquireLock_nanos_per_event": Stat("gauge", "scheduler_thrift_acquireLock_nanos_per_event"),
    "scheduler_thrift_acquireLock_nanos_total": Stat("counter", "scheduler_thrift_acquireLock_nanos_total"),
    "scheduler_thrift_acquireLock_nanos_total_per_sec": Stat("gauge",
                                                             "scheduler_thrift_acquireLock_nanos_total_per_sec"),
    "scheduler_thrift_addInstances_events": Stat("counter", "scheduler_thrift_addInstances_events"),
    "scheduler_thrift_addInstances_events_per_sec": Stat("gauge", "scheduler_thrift_addInstances_events_per_sec"),
    "scheduler_thrift_addInstances_nanos_per_event": Stat("gauge", "scheduler_thrift_addInstances_nanos_per_event"),
    "scheduler_thrift_addInstances_nanos_total": Stat("counter", "scheduler_thrift_addInstances_nanos_total"),
    "scheduler_thrift_addInstances_nanos_total_per_sec": Stat("gauge",
                                                              "scheduler_thrift_addInstances_nanos_total_per_sec"),
    "scheduler_thrift_createJob_events": Stat("gauge", "scheduler_thrift_createJob_events"),
    "scheduler_thrift_createJob_events_per_sec": Stat("gauge", "scheduler_thrift_createJob_events_per_sec"),
    "scheduler_thrift_createJob_nanos_per_event": Stat("gauge", "scheduler_thrift_createJob_nanos_per_event"),
    "scheduler_thrift_createJob_nanos_total": Stat("counter", "scheduler_thrift_createJob_nanos_total"),
    "scheduler_thrift_createJob_nanos_total_per_sec": Stat("gauge", "scheduler_thrift_createJob_nanos_total_per_sec"),
    "scheduler_thrift_descheduleCronJob_events": Stat("gauge", "scheduler_thrift_descheduleCronJob_events"),
    "scheduler_thrift_descheduleCronJob_events_per_sec": Stat("gauge",
                                                              "scheduler_thrift_descheduleCronJob_events_per_sec"),
    "scheduler_thrift_descheduleCronJob_nanos_per_event": Stat("gauge",
                                                               "scheduler_thrift_descheduleCronJob_nanos_per_event"),
    "scheduler_thrift_descheduleCronJob_nanos_total": Stat("counter", "scheduler_thrift_descheduleCronJob_nanos_total"),
    "scheduler_thrift_descheduleCronJob_nanos_total_per_sec": Stat("gauge",
                                                                   "scheduler_thrift_descheduleCronJob_nanos_total_per_sec"),
    "scheduler_thrift_getConfigSummary_events": Stat("counter", "scheduler_thrift_getConfigSummary_events"),
    "scheduler_thrift_getConfigSummary_events_per_sec": Stat("gauge",
                                                             "scheduler_thrift_getConfigSummary_events_per_sec"),
    "scheduler_thrift_getConfigSummary_nanos_per_event": Stat("gauge",
                                                              "scheduler_thrift_getConfigSummary_nanos_per_event"),
    "scheduler_thrift_getConfigSummary_nanos_total": Stat("counter", "scheduler_thrift_getConfigSummary_nanos_total"),
    "scheduler_thrift_getConfigSummary_nanos_total_per_sec": Stat("gauge",
                                                                  "scheduler_thrift_getConfigSummary_nanos_total_per_sec"),
    "scheduler_thrift_getJobSummary_events": Stat("counter", "scheduler_thrift_getJobSummary_events"),
    "scheduler_thrift_getJobSummary_events_per_sec": Stat("gauge", "scheduler_thrift_getJobSummary_events_per_sec"),
    "scheduler_thrift_getJobSummary_nanos_per_event": Stat("gauge", "scheduler_thrift_getJobSummary_nanos_per_event"),
    "scheduler_thrift_getJobSummary_nanos_total": Stat("counter", "scheduler_thrift_getJobSummary_nanos_total"),
    "scheduler_thrift_getJobSummary_nanos_total_per_sec": Stat("gauge",
                                                               "scheduler_thrift_getJobSummary_nanos_total_per_sec"),
    "scheduler_thrift_getJobUpdateSummaries_events": Stat("counter", "scheduler_thrift_getJobUpdateSummaries_events"),
    "scheduler_thrift_getJobUpdateSummaries_events_per_sec": Stat("gauge",
                                                                  "scheduler_thrift_getJobUpdateSummaries_events_per_sec"),
    "scheduler_thrift_getJobUpdateSummaries_nanos_per_event": Stat("gauge",
                                                                   "scheduler_thrift_getJobUpdateSummaries_nanos_per_event"),
    "scheduler_thrift_getJobUpdateSummaries_nanos_total": Stat("counter",
                                                               "scheduler_thrift_getJobUpdateSummaries_nanos_total"),
    "scheduler_thrift_getJobUpdateSummaries_nanos_total_per_sec": Stat("gauge",
                                                                       "scheduler_thrift_getJobUpdateSummaries_nanos_total_per_sec"),
    "scheduler_thrift_getJobs_events": Stat("gauge", "scheduler_thrift_getJobs_events"),
    "scheduler_thrift_getJobs_events_per_sec": Stat("gauge", "scheduler_thrift_getJobs_events_per_sec"),
    "scheduler_thrift_getJobs_nanos_per_event": Stat("gauge", "scheduler_thrift_getJobs_nanos_per_event"),
    "scheduler_thrift_getJobs_nanos_total": Stat("counter", "scheduler_thrift_getJobs_nanos_total"),
    "scheduler_thrift_getJobs_nanos_total_per_sec": Stat("gauge", "scheduler_thrift_getJobs_nanos_total_per_sec"),
    "scheduler_thrift_getPendingReason_events": Stat("counter", "scheduler_thrift_getPendingReason_events"),
    "scheduler_thrift_getPendingReason_events_per_sec": Stat("gauge",
                                                             "scheduler_thrift_getPendingReason_events_per_sec"),
    "scheduler_thrift_getPendingReason_nanos_per_event": Stat("gauge",
                                                              "scheduler_thrift_getPendingReason_nanos_per_event"),
    "scheduler_thrift_getPendingReason_nanos_total": Stat("counter", "scheduler_thrift_getPendingReason_nanos_total"),
    "scheduler_thrift_getPendingReason_nanos_total_per_sec": Stat("gauge",
                                                                  "scheduler_thrift_getPendingReason_nanos_total_per_sec"),
    "scheduler_thrift_getQuota_events": Stat("counter", "scheduler_thrift_getQuota_events"),
    "scheduler_thrift_getQuota_events_per_sec": Stat("gauge", "scheduler_thrift_getQuota_events_per_sec"),
    "scheduler_thrift_getQuota_nanos_per_event": Stat("gauge", "scheduler_thrift_getQuota_nanos_per_event"),
    "scheduler_thrift_getQuota_nanos_total": Stat("counter", "scheduler_thrift_getQuota_nanos_total"),
    "scheduler_thrift_getQuota_nanos_total_per_sec": Stat("gauge", "scheduler_thrift_getQuota_nanos_total_per_sec"),
    "scheduler_thrift_getRoleSummary_events": Stat("gauge", "scheduler_thrift_getRoleSummary_events"),
    "scheduler_thrift_getRoleSummary_events_per_sec": Stat("gauge", "scheduler_thrift_getRoleSummary_events_per_sec"),
    "scheduler_thrift_getRoleSummary_nanos_per_event": Stat("gauge", "scheduler_thrift_getRoleSummary_nanos_per_event"),
    "scheduler_thrift_getRoleSummary_nanos_total": Stat("counter", "scheduler_thrift_getRoleSummary_nanos_total"),
    "scheduler_thrift_getRoleSummary_nanos_total_per_sec": Stat("gauge",
                                                                "scheduler_thrift_getRoleSummary_nanos_total_per_sec"),
    "scheduler_thrift_getTasksStatus_events": Stat("gauge", "scheduler_thrift_getTasksStatus_events"),
    "scheduler_thrift_getTasksStatus_events_per_sec": Stat("gauge", "scheduler_thrift_getTasksStatus_events_per_sec"),
    "scheduler_thrift_getTasksStatus_nanos_per_event": Stat("gauge", "scheduler_thrift_getTasksStatus_nanos_per_event"),
    "scheduler_thrift_getTasksStatus_nanos_total": Stat("counter", "scheduler_thrift_getTasksStatus_nanos_total"),
    "scheduler_thrift_getTasksStatus_nanos_total_per_sec": Stat("gauge",
                                                                "scheduler_thrift_getTasksStatus_nanos_total_per_sec"),
    "scheduler_thrift_getTasksWithoutConfigs_events": Stat("counter", "scheduler_thrift_getTasksWithoutConfigs_events"),
    "scheduler_thrift_getTasksWithoutConfigs_events_per_sec": Stat("gauge",
                                                                   "scheduler_thrift_getTasksWithoutConfigs_events_per_sec"),
    "scheduler_thrift_getTasksWithoutConfigs_nanos_per_event": Stat("gauge",
                                                                    "scheduler_thrift_getTasksWithoutConfigs_nanos_per_event"),
    "scheduler_thrift_getTasksWithoutConfigs_nanos_total": Stat("counter",
                                                                "scheduler_thrift_getTasksWithoutConfigs_nanos_total"),
    "scheduler_thrift_getTasksWithoutConfigs_nanos_total_per_sec": Stat("gauge",
                                                                        "scheduler_thrift_getTasksWithoutConfigs_nanos_total_per_sec"),
    "scheduler_thrift_killTasks_events": Stat("counter", "scheduler_thrift_killTasks_events"),
    "scheduler_thrift_killTasks_events_per_sec": Stat("gauge", "scheduler_thrift_killTasks_events_per_sec"),
    "scheduler_thrift_killTasks_nanos_per_event": Stat("gauge", "scheduler_thrift_killTasks_nanos_per_event"),
    "scheduler_thrift_killTasks_nanos_total": Stat("counter", "scheduler_thrift_killTasks_nanos_total"),
    "scheduler_thrift_killTasks_nanos_total_per_sec": Stat("gauge", "scheduler_thrift_killTasks_nanos_total_per_sec"),
    "scheduler_thrift_populateJobConfig_events": Stat("gauge", "scheduler_thrift_populateJobConfig_events"),
    "scheduler_thrift_populateJobConfig_events_per_sec": Stat("gauge",
                                                              "scheduler_thrift_populateJobConfig_events_per_sec"),
    "scheduler_thrift_populateJobConfig_nanos_per_event": Stat("gauge",
                                                               "scheduler_thrift_populateJobConfig_nanos_per_event"),
    "scheduler_thrift_populateJobConfig_nanos_total": Stat("counter", "scheduler_thrift_populateJobConfig_nanos_total"),
    "scheduler_thrift_populateJobConfig_nanos_total_per_sec": Stat("gauge",
                                                                   "scheduler_thrift_populateJobConfig_nanos_total_per_sec"),
    "scheduler_thrift_releaseLock_events": Stat("gauge", "scheduler_thrift_releaseLock_events"),
    "scheduler_thrift_releaseLock_events_per_sec": Stat("gauge", "scheduler_thrift_releaseLock_events_per_sec"),
    "scheduler_thrift_releaseLock_nanos_per_event": Stat("gauge", "scheduler_thrift_releaseLock_nanos_per_event"),
    "scheduler_thrift_releaseLock_nanos_total": Stat("counter", "scheduler_thrift_releaseLock_nanos_total"),
    "scheduler_thrift_releaseLock_nanos_total_per_sec": Stat("gauge",
                                                             "scheduler_thrift_releaseLock_nanos_total_per_sec"),
    "scheduler_thrift_scheduleCronJob_events": Stat("gauge", "scheduler_thrift_scheduleCronJob_events"),
    "scheduler_thrift_scheduleCronJob_events_per_sec": Stat("gauge", "scheduler_thrift_scheduleCronJob_events_per_sec"),
    "scheduler_thrift_scheduleCronJob_nanos_per_event": Stat("gauge",
                                                             "scheduler_thrift_scheduleCronJob_nanos_per_event"),
    "scheduler_thrift_scheduleCronJob_nanos_total": Stat("counter", "scheduler_thrift_scheduleCronJob_nanos_total"),
    "scheduler_thrift_scheduleCronJob_nanos_total_per_sec": Stat("gauge",
                                                                 "scheduler_thrift_scheduleCronJob_nanos_total_per_sec"),
    "scheduling_veto_dynamic": Stat("counter", "scheduling_veto_dynamic"),
    "scheduling_veto_static": Stat("counter", "scheduling_veto_static"),
    # SLA
    "sla_cluster_mtta_ms": Stat("gauge", "sla_cluster_mtta_ms"),
    "sla_cluster_mtta_nonprod_ms": Stat("gauge", "sla_cluster_mtta_nonprod_ms"),
    "sla_cluster_mttr_ms": Stat("gauge", "sla_cluster_mttr_ms"),
    "sla_cluster_mttr_nonprod_ms": Stat("gauge", "sla_cluster_mttr_nonprod_ms"),
    "sla_cluster_platform_uptime_percent": Stat("gauge", "sla_cluster_platform_uptime_percent"),
    "sla_cpu_small_mtta_ms": Stat("gauge", "sla_cpu_small_mtta_ms"),
    "sla_cpu_small_mtta_nonprod_ms": Stat("gauge", "sla_cpu_small_mtta_nonprod_ms"),
    "sla_cpu_small_mttr_ms": Stat("gauge", "sla_cpu_small_mttr_ms"),
    "sla_cpu_small_mttr_nonprod_ms": Stat("gauge", "sla_cpu_small_mttr_nonprod_ms"),
    "sla_disk_small_mtta_ms": Stat("gauge", "sla_disk_small_mtta_ms"),
    "sla_disk_small_mtta_nonprod_ms": Stat("gauge", "sla_disk_small_mtta_nonprod_ms"),
    "sla_disk_small_mttr_ms": Stat("gauge", "sla_disk_small_mttr_ms"),
    "sla_disk_small_mttr_nonprod_ms": Stat("gauge", "sla_disk_small_mttr_nonprod_ms"),
    "sla_ram_medium_mtta_nonprod_ms": Stat("gauge", "sla_ram_medium_mtta_nonprod_ms"),
    "sla_ram_medium_mttr_nonprod_ms": Stat("gauge", "sla_ram_medium_mttr_nonprod_ms"),
    "sla_ram_small_mtta_ms": Stat("gauge", "sla_ram_small_mtta_ms"),
    "sla_ram_small_mtta_nonprod_ms": Stat("gauge", "sla_ram_small_mtta_nonprod_ms"),
    "sla_ram_small_mttr_ms": Stat("gauge", "sla_ram_small_mttr_ms"),
    "sla_ram_small_mttr_nonprod_ms": Stat("gauge", "sla_ram_small_mttr_nonprod_ms"),
    "sla_stats_computation_events": Stat("counter", "sla_stats_computation_events"),
    "sla_stats_computation_events_per_sec": Stat("gauge", "sla_stats_computation_events_per_sec"),
    "sla_stats_computation_nanos_per_event": Stat("gauge", "sla_stats_computation_nanos_per_event"),
    "sla_stats_computation_nanos_total": Stat("counter", "sla_stats_computation_nanos_total"),
    "sla_stats_computation_nanos_total_per_sec": Stat("gauge", "sla_stats_computation_nanos_total_per_sec"),
    # Snapshot
    "snapshot_apply_events": Stat("gauge", "snapshot_apply_events"),
    "snapshot_apply_events_per_sec": Stat("gauge", "snapshot_apply_events_per_sec"),
    "snapshot_apply_nanos_per_event": Stat("gauge", "snapshot_apply_nanos_per_event"),
    "snapshot_apply_nanos_total": Stat("counter", "snapshot_apply_nanos_total"),
    "snapshot_apply_nanos_total_per_sec": Stat("gauge", "snapshot_apply_nanos_total_per_sec"),
    "snapshot_create_events": Stat("counter", "snapshot_create_events"),
    "snapshot_create_events_per_sec": Stat("gauge", "snapshot_create_events_per_sec"),
    "snapshot_create_nanos_per_event": Stat("gauge", "snapshot_create_nanos_per_event"),
    "snapshot_create_nanos_total": Stat("counter", "snapshot_create_nanos_total"),
    "snapshot_create_nanos_total_per_sec": Stat("gauge", "snapshot_create_nanos_total_per_sec"),
    # Sys
    "system_env_SHLVL": Stat("gauge", "system_env_SHLVL"),
    "system_free_physical_memory_mb": Stat("counter", "system_free_physical_memory_mb"),
    "system_free_swap_mb": Stat("gauge", "system_free_swap_mb"),
    "system_load_avg": Stat("gauge", "system_load_avg"),
    # Task
    "task_delivery_delay_SOURCE_MASTER_requests_per_sec": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_requests_per_sec"),
    "task_delivery_delay_SOURCE_MASTER_requests_micros_total": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_requests_micros_total"),
    "task_delivery_delay_SOURCE_MASTER_requests_micros_per_event": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_requests_micros_per_event"),
    "task_delivery_delay_SOURCE_MASTER_99_0_percentile": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_99_0_percentile"),
    "task_delivery_delay_SOURCE_MASTER_timeouts_per_sec": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_timeouts_per_sec"),
    "task_delivery_delay_SOURCE_MASTER_99_9_percentile": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_99_9_percentile"),
    "task_delivery_delay_SOURCE_MASTER_requests_events": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_requests_events"),
    "scheduler_thrift_replaceCronTemplate_events": Stat("gauge", "scheduler_thrift_replaceCronTemplate_events"),
    "task_delivery_delay_SOURCE_MASTER_errors": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_errors"),
    "task_delivery_delay_SOURCE_MASTER_90_0_percentile": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_90_0_percentile"),
    "scheduler_thrift_replaceCronTemplate_nanos_total": Stat("gauge", "scheduler_thrift_replaceCronTemplate_nanos_total"),
    "task_delivery_delay_SOURCE_MASTER_requests_micros_total_per_sec": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_requests_micros_total_per_sec"),
    "task_delivery_delay_SOURCE_MASTER_99_99_percentile": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_99_99_percentile"),
    "task_delivery_delay_SOURCE_MASTER_reconnects": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_reconnects"),
    "task_delivery_delay_SOURCE_MASTER_error_rate": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_error_rate"),
    "scheduler_thrift_replaceCronTemplate_nanos_total_per_sec": Stat("gauge", "scheduler_thrift_replaceCronTemplate_nanos_total_per_sec"),
    "task_delivery_delay_SOURCE_MASTER_50_0_percentile": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_50_0_percentile"),
    "task_delivery_delay_SOURCE_MASTER_10_0_percentile": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_10_0_percentile"),
    "task_delivery_delay_SOURCE_MASTER_timeouts": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_timeouts"),
    "task_delivery_delay_SOURCE_MASTER_timeout_rate": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_timeout_rate"),
    "task_delivery_delay_SOURCE_MASTER_errors_per_sec": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_errors_per_sec"),
    "scheduler_thrift_replaceCronTemplate_nanos_per_event": Stat("gauge", "scheduler_thrift_replaceCronTemplate_nanos_per_event"),
    "scheduler_thrift_replaceCronTemplate_events_per_sec": Stat("gauge", "scheduler_thrift_replaceCronTemplate_events_per_sec"),
    "task_delivery_delay_SOURCE_MASTER_requests_events_per_sec": Stat("gauge", "task_delivery_delay_SOURCE_MASTER_requests_events_per_sec"),
    "task_config_keys_backfilled": Stat("gauge", "task_config_keys_backfilled"),
    "task_exit_REASON_COMMAND_EXECUTOR_FAILED": Stat("counter", "task_exit_REASON_COMMAND_EXECUTOR_FAILED"),
    "task_exit_REASON_EXECUTOR_TERMINATED": Stat("counter", "task_exit_REASON_EXECUTOR_TERMINATED"),
    "task_exit_REASON_SLAVE_REMOVED": Stat("gauge", "task_exit_REASON_SLAVE_REMOVED"),
    "task_kill_retries": Stat("gauge", "task_kill_retries"),
    "task_lost_SOURCE_MASTER": Stat("gauge", "task_lost_SOURCE_MASTER"),
    "task_lost_SOURCE_SLAVE": Stat("counter", "task_lost_SOURCE_SLAVE"),
    "task_queries_all": Stat("counter", "task_queries_all"),
    "task_queries_by_host": Stat("counter", "task_queries_by_host"),
    "task_queries_by_id": Stat("counter", "task_queries_by_id"),
    "task_queries_by_job": Stat("counter", "task_queries_by_job"),
    "task_schedule_attempt_events": Stat("counter", "task_schedule_attempt_events"),
    "task_schedule_attempt_events_per_sec": Stat("gauge", "task_schedule_attempt_events_per_sec"),
    "task_schedule_attempt_locked_events": Stat("counter", "task_schedule_attempt_locked_events"),
    "task_schedule_attempt_locked_events_per_sec": Stat("gauge", "task_schedule_attempt_locked_events_per_sec"),
    "task_schedule_attempt_locked_nanos_per_event": Stat("gauge", "task_schedule_attempt_locked_nanos_per_event"),
    "task_schedule_attempt_locked_nanos_total": Stat("counter", "task_schedule_attempt_locked_nanos_total"),
    "task_schedule_attempt_locked_nanos_total_per_sec": Stat("gauge",
                                                             "task_schedule_attempt_locked_nanos_total_per_sec"),
    "task_schedule_attempt_nanos_per_event": Stat("gauge", "task_schedule_attempt_nanos_per_event"),
    "task_schedule_attempt_nanos_total": Stat("counter", "task_schedule_attempt_nanos_total"),
    "task_schedule_attempt_nanos_total_per_sec": Stat("gauge", "task_schedule_attempt_nanos_total_per_sec"),
    "task_store_ASSIGNED": Stat("gauge", "task_store_ASSIGNED"),
    "task_store_DRAINING": Stat("gauge", "task_store_DRAINING"),
    "task_store_FAILED": Stat("counter", "task_store_FAILED"),
    "task_store_FINISHED": Stat("counter", "task_store_FINISHED"),
    "task_store_INIT": Stat("gauge", "task_store_INIT"),
    "task_store_KILLED": Stat("counter", "task_store_KILLED"),
    "task_store_KILLING": Stat("gauge", "task_store_KILLING"),
    "task_store_LOST": Stat("counter", "task_store_LOST"),
    "task_store_PENDING": Stat("gauge", "task_store_PENDING"),
    "task_store_PREEMPTING": Stat("gauge", "task_store_PREEMPTING"),
    "task_store_RESTARTING": Stat("gauge", "task_store_RESTARTING"),
    "task_store_RUNNING": Stat("counter", "task_store_RUNNING"),
    "task_store_STARTING": Stat("gauge", "task_store_STARTING"),
    "task_store_THROTTLED": Stat("gauge", "task_store_THROTTLED"),
    "task_throttle_events": Stat("counter", "task_throttle_events"),
    "task_throttle_events_per_sec": Stat("gauge", "task_throttle_events_per_sec"),
    "task_throttle_ms_per_event": Stat("gauge", "task_throttle_ms_per_event"),
    "task_throttle_ms_total": Stat("counter", "task_throttle_ms_total"),
    "task_throttle_ms_total_per_sec": Stat("gauge", "task_throttle_ms_total_per_sec"),
    "timed_out_tasks": Stat("gauge", "timed_out_tasks"),
    "timeout_queue_size": Stat("counter", "timeout_queue_size"),
    # Uncaught Exeptions
    "uncaught_exceptions": Stat("gauge", "uncaught_exceptions"),
    # variable_scrape
    "variable_scrape_events": Stat("counter", "variable_scrape_events"),
    "variable_scrape_events_per_sec": Stat("gauge", "variable_scrape_events_per_sec"),
    "variable_scrape_micros_per_event": Stat("gauge", "variable_scrape_micros_per_event"),
    "variable_scrape_micros_total": Stat("counter", "variable_scrape_micros_total"),
    "variable_scrape_micros_total_per_sec": Stat("gauge", "variable_scrape_micros_total_per_sec"),
}

DYNAMIC_STAT_LIST = {
    "sla_": {
        "_job_uptime_50.00_sec": Stat("counter", "_job_uptime_50_sec"),
        "_job_uptime_75.00_sec": Stat("counter", "_job_uptime_75_sec"),
        "_job_uptime_90.00_sec": Stat("counter", "_job_uptime_90_sec"),
        "_job_uptime_95.00_sec": Stat("counter", "_job_uptime_95_sec"),
        "_job_uptime_99.00_sec": Stat("counter", "_job_uptime_99_sec"),
        "_mtta_ms": Stat("gauge", "_mtta_ms"),
        "_mtta_nonprod_ms": Stat("gauge", "_mtta_nonprod_ms"),
        "_mttr_ms": Stat("gauge", "_mttr_ms"),
        "_mttr_nonprod_ms": Stat("gauge", "_mttr_nonprod_ms"),
        "_platform_uptime_percent": Stat("gauge", "_platform_uptime_percent")
    },
    "tasks_": {
        "tasks_FAILED_": Stat("counter", "tasks_FAILED_" + TASK_ID),
        "tasks_LOST_": Stat("counter", "tasks_LOST_" + TASK_ID),
        "tasks_lost_rack_": Stat("counter", "tasks_lost_rack_" + RACK_ID),
    }
}

DYNAMIC_STATS = ['sla_' + TASK_ID, 'tasks_FAILED_' + TASK_ID, 'tasks_lost_rack_' + RACK_ID,
                 'tasks_lost_rack_' + RACK_ID]


def configure_callback(conf):
    host = 'localhost'
    port = 8081
    username = None
    password = None
    instance = ''
    path = '/vars'
    scheme = 'http'

    for node in conf.children:
        key = node.key.lower()
        val = node.values[0]

        if key == 'host':
            host = val
        elif key == 'port':
            port = int(val)
        elif key == 'verbose':
            global VERBOSE_LOGGING
            VERBOSE_LOGGING = bool(node.values[0]) or VERBOSE_LOGGING
        elif key == 'instance':
            instance = val
        elif key == 'path':
            path = val
        elif key == 'username':
            username = val
        elif key == 'password':
            password = val
        elif key == 'ssl':
            scheme = 'https' if bool(node.values[0]) else 'http'
        else:
            collectd.warning('{} plugin: Unknown config key: {}.'.format(COLLECTD_PLUGIN_NAMESPACE, key))
            continue

    log_message(
        'Configured with host={host}, port={port}, instance name={instance}, using_auth={auth}'.format(
            host=host, port=port, instance=instance, auth=(username != None)),
        verbose=True)

    CONFIGS.append(
        {'host': host, 'port': port, 'username': username, 'password': password, 'instance': instance, 'path': path,
         'scheme': scheme})


def get_metric(t):
    type_instance = None
    if t not in METRICS:
        # Following is a hack, I will think on this later for a more elegant solution
        # Todo revisit
        v = None
        if 'sla_' in t[0:4]:
            for k, v in DYNAMIC_STAT_LIST['sla_'].iteritems():
                if k in t[4:]:
                    v = Stat('counter', (v.type, t))
            type_instance = 'sla'
        elif 'tasks_FAILED_' in t:
            v = DYNAMIC_STAT_LIST['tasks_']['tasks_FAILED_']
            v = Stat('counter', (v.type, t))
            type_instance = t
        elif 'tasks_LOST_' in t:
            v = DYNAMIC_STAT_LIST['tasks_']['tasks_LOST_']
            v = Stat('counter', (v.type, t))
            type_instance = t
        elif 'tasks_lost_rack_' in t:
            v = DYNAMIC_STAT_LIST['tasks_']['tasks_lost_rack_']
            v = Stat('counter', (v.type, t))
            type_instance = t
        return v, type_instance
    else:
        return METRICS[t], type_instance


def read_callback():
    for conf in CONFIGS:
        get_metrics(conf)


def get_metrics(conf):
    plugin_instance = conf['instance']

    results = fetch_info(scheme=conf['scheme'], host=conf['host'], path=conf['path'], port=conf['port'])
    for key, value in results.iteritems():
        metric, type_instance = get_metric(key)
        if metric is not None:
            dispatch_stat(value, metric.name, metric.type, plugin_instance, type_instance)


def dispatch_stat(value, name, type, plugin_instance=None, type_instance=None):
    try:
        if value is None:
            collectd.warning('{} plugin: Value not found for {}'.format(COLLECTD_PLUGIN_NAMESPACE, name))
            return
        if not type_instance:
            type_instance = name
        log_message('{} plugin: sending value[{}]: {}={}'.format(COLLECTD_PLUGIN_NAMESPACE, type, name, value),verbose=True)
        val = collectd.Values(plugin = COLLECTD_PLUGIN_NAMESPACE)
        val.type = type
        val.type_instance = type_instance
        val.plugin_instance = plugin_instance
        val.values = [value]
        val.dispatch()
    except NameError:
        print {'value': value, 'name': name, 'metric_type': type, 'plugin_instance': plugin_instance,
               'type_instance': type_instance}


def fetch_info(host, port, path="/vars", scheme="http", username=None, password=None):
    result_set = {}
    auth = None
    try:
        if username and password:
            auth = requests.auth.HTTPBasicAuth(username=username, password=password)
        REQUEST_URI = "{scheme}://{host}:{port}{path}.json".format(scheme=scheme,
                        host=host, port=port, path=path)
        result = requests.get(REQUEST_URI, auth=auth)
        return result.json()
    except RETRIABLE_EXCEPTIONS, exc:
        log_message(exc.message)
        return None
    except Exception, exc:
        log_message(exc.message)
        return None


def log_message(msg, verbose=True):
    if verbose and not VERBOSE_LOGGING:
        return
    elif verbose and VERBOSE_LOGGING:
        try:
            collectd.info('aurora plugin [verbose]: %s'.format(msg))
        except NameError:
            sys.stderr.write('aurora plugin [verbose]: %s'.format(msg))
    else:
        try:
            collectd.info(msg)
        except NameError:
            sys.stderr.write(msg)


def test_parserer():
    fixture_data = [
        "tasks_FAILED_root/prod/my-application",
        "tasks_LOST_root/prod/my-application",
        "tasks_lost_rack_us_east_1b",
        "sla_root/prod/my-application_job_uptime_50.00_sec",
        "sla_root/prod/my-application_job_uptime_75.00_sec",
        "sla_root/prod/my.application_job_uptime_90.00_sec",
        "sla_root/prod/my-application_job_uptime_95.00_sec",
        "sla_root/devel/my-application_job_uptime_99.00_sec",
        "sla_root/staging0/my_application_mtta_ms",
        "sla_root/test/my-application_mtta_nonprod_ms",
        "sla_root/prod/my-application_mttr_ms",
        "sla_root/prod/my-application_mttr_nonprod_ms",
        "sla_root/prod/my-application_platform_uptime_percent"
    ]
    for t in fixture_data:
        metric, type_instance = get_metric(t)
        assert type(metric) is Stat, "Assertion for metric '{}'".format(metric)
        if 'sla_' in t[:4]:
            assert type_instance == 'sla'


# register callbacks
try:
    collectd.register_config(configure_callback)
    collectd.register_read(read_callback)
except NameError, exc:
    if __name__ != '__main__':
        import sys

        sys.stderr.write(exc.message)
        sys.stderr.flush()

