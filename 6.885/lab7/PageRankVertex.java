package test;
/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */



import org.apache.giraph.Algorithm;
import org.apache.giraph.conf.LongConfOption;
import org.apache.giraph.edge.Edge;
import org.apache.giraph.graph.Vertex;
import org.apache.hadoop.io.DoubleWritable;
import org.apache.hadoop.io.FloatWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.log4j.Logger;

@Algorithm(
    name = "Page Rank",
    description = "Gets the page rank for all vertices in a graph"
)
public class PageRankVertex extends
    Vertex<LongWritable, DoubleWritable,
    FloatWritable, DoubleWritable> {
  /** Class logger */
  private static final Logger LOG =
      Logger.getLogger(PageRankVertex.class);

  public static final int MAX_SUPERSTEPS = 30;

  public static final double DAMPING_FACTOR = 0.5;

  private double initializationValue() {
    return 1f / getTotalNumVertices();
  }

  @Override
  public void compute(Iterable<DoubleWritable> messages) {
    if (getSuperstep() == 1) {
      setValue(new DoubleWritable(1.0f / getTotalNumVertices()));
    } else {
      double sum = 0;
      for (DoubleWritable message : messages) {
        sum += message.get();
      }

      DoubleWritable vertexValue = new DoubleWritable((1.0f - DAMPING_FACTOR) + (DAMPING_FACTOR * sum));
      setValue(vertexValue);
      if (LOG.isDebugEnabled()) {
        LOG.debug("Vertex " + getId() + " got Sum = " + sum +
            " vertex value = " + getValue());
      }
    }


    if (getSuperstep() <= MAX_SUPERSTEPS) {
      DoubleWritable value = new DoubleWritable(getValue() / getNumEdges());
      for (Edge<IntWritable, NullWritable> edge : getEdges()) {
        if (LOG.isDebugEnabled()) {
          LOG.debug("Vertex " + getId() + " sent to " + 
              edge.getTargetVertexId() + " = " + value);
        }
        sendMessage(edge.getTargetVertexId(), value);
      }
    } else {
      voteToHalt();
    }
  }
}
