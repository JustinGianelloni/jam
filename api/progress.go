package api

type ProgressFunc func(completed, total int)

func TrackProgress(pageDone <-chan struct{}, totalPages int, progress ProgressFunc) <-chan struct{} {
	finished := make(chan struct{})
	go func() {
		defer close(finished)
		completed := 1
		for range pageDone {
			completed++
			if progress != nil {
				progress(completed, totalPages)
			}
		}
	}()
	return finished
}
