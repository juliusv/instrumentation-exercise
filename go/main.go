package main

import (
	"flag"
	"log"
	"math/rand"
	"net/http"
	"time"

	"github.com/prometheus/client_golang/prometheus"
)

type demoAPI struct {
	requestDurations *prometheus.HistogramVec
}

func newDemoAPI(reg prometheus.Registerer) *demoAPI {
	return &demoAPI{
		requestDurations: prometheus.NewHistogramVec(prometheus.HistogramOpts{
			Name:    "some_api_http_request_duration_seconds",
			Help:    "A histogram of the demo API request durations in seconds.",
			Buckets: prometheus.LinearBuckets(.05, .025, 10),
		}, []string{"handler"}),
	}
}

func (a demoAPI) register(mux *http.ServeMux) {
	instr := func(handler string, fn http.HandlerFunc) http.HandlerFunc {
		return func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			fn(w, r)
			a.requestDurations.WithLabelValues(handler).Observe(float64(time.Since(start)))
		}
	}

	mux.HandleFunc("/api/foo", instr("foo", a.foo))
	mux.HandleFunc("/api/bar", instr("bar", a.bar))
}

func (a demoAPI) foo(w http.ResponseWriter, r *http.Request) {
	log.Println("Handling foo...")

	// Simulate a random duration that the "foo" operation needs to be completed.
	time.Sleep(75*time.Millisecond + time.Duration(rand.Float64())*50*time.Millisecond)

	w.Write([]byte("Handled foo"))
}

func (a demoAPI) bar(w http.ResponseWriter, r *http.Request) {
	log.Println("Handling bar...")
	// Simulate a random duration that the "bar" operation needs to be completed.
	time.Sleep(150*time.Millisecond + time.Duration(rand.Float64())*100*time.Millisecond)

	w.Write([]byte("Handled bar"))
}

func backgroundTask(reg prometheus.Registerer) {
	totalCount := prometheus.NewCounter(prometheus.CounterOpts{
		Name: "background_task_runs_total",
		Help: "The total number of background task runs.",
	})
	failureCount := prometheus.NewCounter(prometheus.CounterOpts{
		Name: "background_task_failures_total",
		Help: "The total number of background task failures.",
	})

	log.Println("Starting background task loop...")
	bgTicker := time.NewTicker(5 * time.Second)
	for {
		log.Println("Performing background task...")
		// Simulate a random duration that the background task needs to be completed.
		time.Sleep(1*time.Second + time.Duration(rand.Float64())*500*time.Millisecond)

		// Simulate the background task either succeeding or failing (with a 30% probability).
		if rand.Float64() > 0.3 {
			log.Println("Background task completed successfully.")
		} else {
			failureCount.Inc()
			log.Println("Background task failed.")
		}
		totalCount.Inc()

		<-bgTicker.C
	}
}

func main() {
	listenAddr := flag.String("web.listen-addr", ":12345", "The address to listen on for web requests.")

	go backgroundTask(prometheus.DefaultRegisterer)

	api := newDemoAPI(prometheus.DefaultRegisterer)
	api.register(http.DefaultServeMux)

	log.Fatal(http.ListenAndServe(*listenAddr, nil))
}
