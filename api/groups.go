package api

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"net/url"
	"strconv"
	"sync"

	"github.com/justingianelloni/jam/models"
)

func (c *Client) userGroupsPage(ctx context.Context, skip int, filters []models.V2Filter) ([]models.UserGroup, int, error) {
	params := url.Values{}
	params.Set("limit", strconv.Itoa(pageLimit))
	params.Set("skip", strconv.Itoa(skip))
	for i, f := range filters {
		params.Set(fmt.Sprintf("filter[%d]", i), f.String())
	}
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/v2/usergroups?"+params.Encode(), nil)
	if err != nil {
		return nil, 0, fmt.Errorf("Building request: %w", err)
	}
	res, err := c.do(ctx, req)
	if err != nil {
		return nil, 0, fmt.Errorf("Executing request: %w", err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return nil, 0, fmt.Errorf("API Error: %s", res.Status)
	}
	total, err := v2TotalCount(res)
	if err != nil {
		return nil, 0, fmt.Errorf("Fetching total count: %w", err)
	}
	var groups []models.UserGroup
	if err := json.NewDecoder(res.Body).Decode(&groups); err != nil {
		return nil, 0, fmt.Errorf("Decoding response: %w", err)
	}
	return groups, total, nil
}

func (c *Client) ListUserGroups(ctx context.Context, filters []models.V2Filter) ([]models.UserGroup, error) {
	first, total, err := c.userGroupsPage(ctx, 0, filters)
	if err != nil {
		return nil, fmt.Errorf("Fetching first page: %w", err)
	}
	groups := make([]models.UserGroup, total)
	copy(groups, first)
	if len(first) >= total {
		return groups, nil
	}
	type result struct {
		skip   int
		groups []models.UserGroup
		err    error
	}
	remaining := ((total + pageLimit - 1) / pageLimit) - 1
	results := make(chan result, remaining)
	var wg sync.WaitGroup
	for skip := pageLimit; skip < total; skip += pageLimit {
		wg.Add(1)
		go func(skip int) {
			defer wg.Done()
			page, _, err := c.userGroupsPage(ctx, skip, filters)
			if err != nil {
				results <- result{skip: skip, err: err}
			}
			results <- result{skip: skip, groups: page}
		}(skip)
	}
	wg.Wait()
	close(results)
	for r := range results {
		if r.err != nil {
			return nil, fmt.Errorf("Fetching page at skip=%d: %w", r.skip, r.err)
		}
		copy(groups[r.skip:], r.groups)
	}
	return groups, nil
}

func (c *Client) GetUserGroup(ctx context.Context, grpID string) (*models.UserGroup, error) {
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/usergroups/"+grpID, nil)
	if err != nil {
		return nil, fmt.Errorf("Building request: %w", err)
	}
	res, err := c.do(ctx, req)
	if err != nil {
		return nil, fmt.Errorf("Executing request: %w", err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("API Error: %s", res.Status)
	}
	var group models.UserGroup
	if err := json.NewDecoder(res.Body).Decode(&group); err != nil {
		return nil, fmt.Errorf("Decoding response: %w", err)
	}
	return &group, nil
}

type member struct {
	ID string `json:"id"`
}

type memberResult struct {
	To member `json:"to"`
}

func (c *Client) groupMembersPage(ctx context.Context, grpID string, skip int) ([]string, int, error) {
	params := url.Values{}
	params.Set("limit", strconv.Itoa(pageLimit))
	params.Set("skip", strconv.Itoa(skip))
	req, err := http.NewRequestWithContext(ctx, http.MethodGet, baseURL+"/v2/usergroups/"+grpID+"/members?"+params.Encode(), nil)
	if err != nil {
		return nil, 0, fmt.Errorf("Building request: %w", err)
	}
	res, err := c.do(ctx, req)
	if err != nil {
		return nil, 0, fmt.Errorf("Executing request: %w", err)
	}
	defer res.Body.Close()
	if res.StatusCode != http.StatusOK {
		return nil, 0, fmt.Errorf("API Error: %s", res.Status)
	}
	total, err := v2TotalCount(res)
	if err != nil {
		return nil, 0, fmt.Errorf("Fetching total count: %w", err)
	}
	var results []memberResult
	if err := json.NewDecoder(res.Body).Decode(&results); err != nil {
		return nil, 0, fmt.Errorf("Decoding Response: %w", err)
	}
	members := make([]string, len(results))
	for i, m := range results {
		members[i] = m.To.ID
	}
	return members, total, nil
}

func (c *Client) UserGroupMembers(ctx context.Context, grpID string) ([]string, error) {
	first, total, err := c.groupMembersPage(ctx, grpID, 0)
	if err != nil {
		return nil, fmt.Errorf("Fetching first page: %w", err)
	}
	members := make([]string, total)
	copy(members, first)
	if len(first) >= total {
		return members, nil
	}
	type result struct {
		skip    int
		members []string
		err     error
	}
	remaining := ((total + pageLimit - 1) / pageLimit) - 1
	results := make(chan result, remaining)
	var wg sync.WaitGroup
	for skip := pageLimit; skip < total; skip += pageLimit {
		wg.Add(1)
		go func(skip int) {
			defer wg.Done()
			page, _, err := c.groupMembersPage(ctx, grpID, skip)
			if err != nil {
				results <- result{skip: skip, err: err}
			}
			results <- result{skip: skip, members: page}
		}(skip)
	}
	wg.Wait()
	close(results)
	for r := range results {
		if r.err != nil {
			return nil, fmt.Errorf("Fetching page at skip=%d: %w", r.skip, r.err)
		}
		copy(members[r.skip:], r.members)
	}
	return members, nil
}
