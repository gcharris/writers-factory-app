## AI Self-Review Document for Creative Prose

This document lists patterns commonly observed in AI-generated text, which can make writing sound generic, exaggerated, or unnaturally formal.

I. Content and Tone Indicators

LLMs tend to regress to the mean, omitting specific, nuanced facts in favor of generic, positive, or exaggerated descriptions. This often leads to issues with neutrality and depth.

| Pattern to Flag                                          | Description & Examples                                       |
| -------------------------------------------------------- | ------------------------------------------------------------ |
| **Exaggerated Importance, Legacy, or Symbolism**         | Flag sections that use overblown language to describe a character, setting, or event, substituting genuine detail for generic positive claims. **Words to watch:** *stands/serves as*, *is a testament/reminder*, *plays a vital/significant/crucial/pivotal role*, *indelible mark*, *profound heritage*. The description may sound like **"a revolutionary titan of industry"** instead of detailing a specific achievement. |
| **Promotional or Advertisement-like Language (Puffery)** | Identify language that sounds like a sales pitch or TV commercial script, as LLMs struggle to maintain a neutral or evocative tone. **Words to watch:** *continues to captivate*, *groundbreaking* (in the figurative sense), *stunning natural beauty*, *enduring/lasting legacy*, *boasts a*. Also flag excessive use of the word **"nestled"** or the phrase **"in the heart of"** when describing locations. |
| **Superficial Analysis using "-ing" Phrases**            | Flag sentences that end with a present participle ("-ing") phrase to insert shallow analysis about what a preceding fact "means". This often creates a claim by a disembodied narrator about the meaning of an event, rather than showing the event’s impact through action or character perspective. **Words to watch:** *ensuring...*, *highlighting...*, *emphasizing...*, *reflecting...*, *underscoring...*, *showcasing...*, *aligns with...*, *contributing to...*. |
| **Didactic or Editorializing Disclaimers**               | Look for statements where the narrator speaks directly to the reader to caution or instruct them on what to think or remember. **Words to watch:** *it's important/critical/crucial to note/remember/consider*. (In creative prose, this breaks the fourth wall with unnecessary formality.) |
| **Formulaic Structuring (Conclusion/Summary)**           | If a scene or chapter ends with a paragraph that unnecessarily summarizes or restates the core idea just covered. **Words to watch:** *In summary*, *In conclusion*, *Overall*. |
| **Formulaic "Challenges and Future Prospects"**          | Flag any sections or paragraphs that follow a rigid outline, such as discussing both the **challenges** and **future outlook** for a person, entity, or concept within the scene. **Words to watch:** *Despite its... faces several challenges...*. |

II. Language and Grammar Indicators

These issues arise from the statistical modeling of LLMs, resulting in predictable vocabulary and sentence structures.

| Pattern to Flag                    | Description & Examples                                       |
| ---------------------------------- | ------------------------------------------------------------ |
| **Overused "AI Vocabulary" Words** | Flag excessive use or concentration of the following terms, as LLMs favor them disproportionately: **crucial**, **pivotal**, **tapestry** (as an abstract noun, e.g., "the rich tapestry of life"), **intricate/intricacies**, **enduring**, **fostering**, **showcase/showcasing**, and **underscore/underscoring**. |
| **Elegant Variation**              | Identify instances where a character or object's primary name is immediately and repeatedly replaced by synonyms (e.g., using "protagonist," "key player," and "eponymous character" interchangeably in close proximity). This stems from the AI's internal repetition-penalty code. |
| **False Ranges**                   | Flag uses of the **"from ... to ..."** construction where the endpoints are loosely related or unrelated, and no coherent scale can be logically inferred. This language is often meaningless but used to impress (e.g., "from the singularity of the Big Bang to the grand cosmic web"). |
| **Rule of Three Overuse**          | Note when the text consistently uses a structure of three points, such as "adjective, adjective, adjective" or "short phrase, short phrase, and short phrase". LLMs overuse this rhetorical device to make superficial points seem comprehensive. |
| **Negative Parallelisms**          | Look for formulaic parallel constructions involving "not," "but," or "however," such as **"Not only ... but ..."** or **"It is not just about ..., it's ... "**. In creative work, this often sounds stilted or overly formal. |
| **Vague Attributions of Opinion**  | While less common in creative prose, flag if claims or opinions are attributed to vague, unnamed authorities. **Words to watch:** *Observers have cited*, *Some critics argue* (unless this is deliberate character dialogue). |

III. General Style and Punctuation Indicators

These patterns affect the visual presentation and rhythm of the text.

| Pattern to Flag                  | Description & Examples                                       |
| -------------------------------- | ------------------------------------------------------------ |
| **Overuse of Em Dashes (—)**     | Identify sections where em dashes are used much more frequently than commas, parentheses, or colons, especially when mimicking a "punched up," sales-like rhythm to over-emphasize clauses. |
| **Curly Quotes and Apostrophes** | Flag the use of **curly quotation marks** (“...”) and **curly apostrophes** (’) instead of the straight versions ("..." and '). While some software converts them (like Microsoft Word or iOS), their presence in raw AI output is typical. |
| **Excessive Use of Boldface**    | Flag passages where phrases are bolded mechanically for emphasis, often mimicking a "key takeaways" or listicle style, rather than emphasizing a critical plot point. |
| **Title Case in Headings**       | If any scene or chapter headings capitalize all main words, this is a style strongly favored by AI chatbots. |

\--------------------------------------------------------------------------------

This guide acts like a **stylistic fingerprint scanner** for your prose. Just as a chef tastes a dish to make sure no single flavor overwhelms the others, using this guide helps ensure that your writing doesn't overly rely on the statistically predictable "flavors" of AI-generated language.